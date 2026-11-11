"""Gera relatório a partir do Postgres: métricas por execução e por classe, consistência,
matriz de confusão, fatias SQL e a lista de erros para análise manual.

  python report.py --prompt v1 --split dev
Saídas: reports/<prompt>_<split>.md e reports/<prompt>_<split>_erros.csv
Preencha a coluna 'causa' do CSV (ambiguidade | vies_modelo | meu_rotulo_errado | prompt_ruim)
e rode de novo: o relatório passa a contar os erros por causa.
"""
import argparse, re
from pathlib import Path
import pandas as pd
from common_path import setup  # noqa: F401
from common.db import connect
from metrics import per_class, accuracy, consistency
from schema import SENTIMENTOS, TEMAS

ROOT = Path(__file__).resolve().parent
INVALIDO = "INVALIDO"

def md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    rows = ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
    rows += ["| " + " | ".join(map(str, r)) + " |" for r in df.itertuples(index=False)]
    return "\n".join(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True); ap.add_argument("--split", required=True)
    a = ap.parse_args()
    params = {"prompt": a.prompt, "split": a.split}
    with connect() as c:
        df = pd.read_sql("""SELECT r.run_idx, r.model, p.review_id, p.valid, p.attempts,
                                   p.sentimento AS pred_s, p.tema AS pred_t,
                                   g.sentimento AS gold_s, g.tema AS gold_t, g.review_text
                            FROM predictions p JOIN runs r USING (run_id) JOIN gold g USING (review_id)
                            WHERE r.prompt_version=%(prompt)s AND r.split=%(split)s""", c, params=params)
        if df.empty:
            raise SystemExit("Nenhuma execução encontrada para esse prompt/split.")
        slices = {}
        sql = (ROOT / "sql/slices.sql").read_text()
        for name, body in re.findall(r"-- name: (\w+)\n(.*?)(?=\n-- name:|\Z)", sql, re.S):
            slices[name] = pd.read_sql(body, c, params=params)
    df["pred_s"] = df.pred_s.fillna(INVALIDO); df["pred_t"] = df.pred_t.fillna(INVALIDO)

    out = [f"# Relatório — prompt `{a.prompt}` no split `{a.split}`\n",
           f"Modelo(s): {', '.join(sorted(df.model.unique()))} · execuções: {df.run_idx.nunique()} · itens: {df.review_id.nunique()}\n"]
    for eixo, gold, pred, labels in [("sentimento", "gold_s", "pred_s", SENTIMENTOS), ("tema", "gold_t", "pred_t", TEMAS)]:
        out.append(f"## {eixo}: acurácia por execução\n")
        accs = [(i, accuracy(g[gold], g[pred])) for i, g in df.groupby("run_idx")]
        out.append(md(pd.DataFrame(accs, columns=["execucao", "acuracia"])))
        out.append(f"\nVariação entre execuções: {min(x for _, x in accs)} a {max(x for _, x in accs)}\n")
        out.append(f"### {eixo}: precisão / recall / F1 por classe (execuções agregadas)\n")
        m = per_class(df[gold], df[pred], labels)
        out.append(md(pd.DataFrame([{"classe": k, **v} for k, v in m.items()])))
        out.append(f"\n### {eixo}: matriz de confusão (linhas = gabarito, colunas = previsão)\n")
        cm = pd.crosstab(df[gold], df[pred]).reindex(index=list(labels)).fillna(0).astype(int)
        out.append(md(cm.reset_index().rename(columns={gold: "gabarito"})))
        runs = [dict(zip(g.review_id, g[pred])) for _, g in df.groupby("run_idx")]
        cons = consistency(runs)
        out.append(f"\nConsistência ({eixo}): {cons['instaveis']} de {cons['itens']} itens mudaram de rótulo entre execuções ({100 - cons['pct_estavel'] if cons['pct_estavel'] is not None else '?'}%).\n")
    for name, s in slices.items():
        out.append(f"## SQL: {name}\n"); out.append(md(s) + "\n")

    err = df[(df.pred_s != df.gold_s) | (df.pred_t != df.gold_t)]
    resumo = (err.groupby("review_id").agg(review_text=("review_text", "first"), gold_s=("gold_s", "first"),
              gold_t=("gold_t", "first"), pred_s=("pred_s", lambda x: "/".join(x)),
              pred_t=("pred_t", lambda x: "/".join(x)), execucoes_com_erro=("run_idx", "nunique")).reset_index())
    resumo["causa"] = ""; resumo["comentario"] = ""
    rep = ROOT / "reports"; rep.mkdir(exist_ok=True)
    csv = rep / f"{a.prompt}_{a.split}_erros.csv"
    if csv.exists():   # preserva o que você já anotou
        old = pd.read_csv(csv, dtype=str).fillna("").set_index("review_id")[["causa", "comentario"]]
        old.index = old.index.astype(int)
        resumo = resumo.set_index("review_id"); resumo.update(old); resumo = resumo.reset_index()
    resumo.to_csv(csv, index=False)
    anot = resumo[resumo.causa != ""]
    out.append(f"## Erros para análise manual\n\n{len(resumo)} itens com erro em ao menos uma execução → `{csv.name}`.\n")
    if len(anot):
        out.append(md(anot.causa.value_counts().rename_axis("causa").reset_index(name="itens")) + "\n")
    else:
        out.append("Ainda sem causas anotadas (preencha a coluna `causa`).\n")
    (rep / f"{a.prompt}_{a.split}.md").write_text("\n".join(out))
    print("\n".join(out[:3]), f"\n→ reports/{a.prompt}_{a.split}.md")

if __name__ == "__main__":
    main()
