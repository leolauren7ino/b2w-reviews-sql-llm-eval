"""Baseline clássico: TF-IDF + regressão logística (scikit-learn) para sentimento.

Pergunta que isto responde: o LLM compensa em relação a um modelo simples, grátis e instantâneo?

Desenho (e o que ele NÃO é):
- Treino: avaliações do B2W com rótulo DERIVADO DAS ESTRELAS (1-2 negativo, 3 neutro, 4-5 positivo),
  sem as 200 do gabarito (nem textos idênticos a elas). Nenhuma chamada de LLM, nenhum Postgres.
- Avaliação: os MESMOS itens de dev/teste do gabarito usados no LLM (mesmo split: seed 42, estratificado),
  cujo rótulo foi feito por Claude lendo o texto. Os dois critérios (estrelas x leitura) não são idênticos:
  parte do "erro" do baseline é discordância entre nota e texto, não falha de modelo.
- Hiperparâmetros fixos, escolhidos antes de ver dev/teste. Nada é ajustado nesses conjuntos.
- Só sentimento: o tema não existe no dataset (só no gabarito), então não há como treinar um baseline de tema
  sem rotular mais dados.

Uso (a partir de projeto2_llm/):
    python baseline_tfidf.py --raw ../data/raw/b2w.csv
"""
import argparse
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from metrics import accuracy, per_class  # noqa: E402
from schema import SENTIMENTOS  # noqa: E402

SEED = 42  # o mesmo do split.py
MIN_LEN, MAX_LEN = 30, 600  # o mesmo filtro do prepare_sample.py


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s)).strip()


def stars_to_sentiment(stars: int) -> str:
    return {1: "negativo", 2: "negativo", 3: "neutro", 4: "positivo", 5: "positivo"}[int(stars)]


def load_gold_splits(labeling_dir: Path) -> dict[str, pd.DataFrame]:
    """Reproduz exatamente o split do split.py, sem precisar do Postgres."""
    df = pd.read_csv(labeling_dir / "to_label.csv")
    stars = pd.read_csv(labeling_dir / "stars_hidden.csv")
    df = df.merge(stars, on="review_id")
    df["review_text"] = df["review_text"].map(norm)
    dev, test = train_test_split(df, test_size=0.5, stratify=df.sentimento, random_state=SEED)
    return {"dev": dev.reset_index(drop=True), "test": test.reset_index(drop=True)}


def load_training(raw_csv: Path, gold_texts: set[str]) -> pd.DataFrame:
    """Treino = B2W bruto, mesmo filtro de tamanho do gabarito, rótulo pelas estrelas,
    sem os textos do gabarito (evita vazamento) e sem textos repetidos."""
    raw = pd.read_csv(raw_csv, usecols=["review_text", "overall_rating"]).dropna()
    raw["review_text"] = raw["review_text"].map(norm)
    raw = raw[raw.review_text.str.len().between(MIN_LEN, MAX_LEN)]
    raw = raw[~raw.review_text.isin(gold_texts)].drop_duplicates("review_text")
    raw["sentimento"] = raw["overall_rating"].map(stars_to_sentiment)
    return raw[["review_text", "sentimento"]].reset_index(drop=True)


def build_model():
    return make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=3, sublinear_tf=True),
        LogisticRegression(max_iter=1000, C=1.0),
    )


def bootstrap_ci(correct: np.ndarray, n_boot: int = 2000, seed: int = 0) -> tuple[float, float]:
    """IC 95% da acurácia por bootstrap. Com 100 itens ele é largo, e é isso que importa mostrar."""
    rng = np.random.default_rng(seed)
    accs = [rng.choice(correct, size=len(correct), replace=True).mean() for _ in range(n_boot)]
    lo, hi = np.percentile(accs, [2.5, 97.5])
    return round(float(lo), 3), round(float(hi), 3)


def evaluate(model, split_df: pd.DataFrame) -> dict:
    t0 = time.perf_counter()
    pred = model.predict(split_df.review_text)
    pred_ms = (time.perf_counter() - t0) * 1000
    truth = split_df.sentimento.to_numpy()
    correct = (pred == truth).astype(float)
    pc = per_class(truth, pred, SENTIMENTOS)
    return {
        "n": len(split_df),
        "accuracy": accuracy(truth, pred),
        "ci95": bootstrap_ci(correct),
        "macro_f1": round(float(np.mean([v["f1"] for v in pc.values()])), 3),
        "per_class": pc,
        "confusion": pd.crosstab(pd.Series(truth, name="gabarito"), pd.Series(pred, name="previsão"))
                       .reindex(index=SENTIMENTOS, columns=SENTIMENTOS, fill_value=0),
        "predict_ms_total": round(pred_ms, 1),
        "pred": pred,
    }


def markdown(split: str, res: dict, info: dict) -> str:
    lines = [
        f"# Baseline TF-IDF + regressão logística — split `{split}`", "",
        f"Treino: {info['n_train']} avaliações (rótulo derivado das estrelas, sem o gabarito) · "
        f"{info['n_features']} features · treino em {info['train_s']} s · "
        f"inferência de {res['n']} itens em {res['predict_ms_total']} ms · custo de API: zero.", "",
        f"Acurácia: **{res['accuracy']}** (IC 95% por bootstrap: {res['ci95'][0]} a {res['ci95'][1]}) · "
        f"F1 macro: {res['macro_f1']}", "",
        "| classe | precision | recall | f1 | support |", "|---|---|---|---|---|",
    ]
    for c, v in res["per_class"].items():
        lines.append(f"| {c} | {v['precision']} | {v['recall']} | {v['f1']} | {v['support']} |")
    lines += ["", "Matriz de confusão (linhas = gabarito rotulado por Claude, colunas = previsão do baseline):", "",
              "| gabarito | " + " | ".join(SENTIMENTOS) + " |", "|---|" + "---|" * len(SENTIMENTOS)]
    for c in SENTIMENTOS:
        lines.append(f"| {c} | " + " | ".join(str(int(x)) for x in res["confusion"].loc[c]) + " |")
    lines += ["", "Atenção: treino por estrelas, avaliação por rótulo de leitura (Claude); ver README do projeto.", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=str(ROOT.parent / "data/raw/b2w.csv"))
    args = ap.parse_args()

    splits = load_gold_splits(ROOT / "labeling")
    gold_texts = set(pd.concat(splits.values()).review_text)
    train = load_training(Path(args.raw), gold_texts)
    print(f"treino: {len(train)} avaliações; distribuição:\n{train.sentimento.value_counts(normalize=True).round(3)}")

    model = build_model()
    t0 = time.perf_counter()
    model.fit(train.review_text, train.sentimento)
    info = {"n_train": len(train), "train_s": round(time.perf_counter() - t0, 1),
            "n_features": len(model[0].vocabulary_)}

    (ROOT / "reports").mkdir(exist_ok=True)
    for name, df in splits.items():
        res = evaluate(model, df)
        out = ROOT / "reports" / f"baseline_tfidf_{name}.md"
        out.write_text(markdown(name, res, info), encoding="utf-8")
        print(f"[{name}] acurácia {res['accuracy']} (IC95 {res['ci95']}), F1 macro {res['macro_f1']} -> {out}")


if __name__ == "__main__":
    main()
