"""Preenche labeling/to_label.csv a partir de um arquivo de texto com seus rótulos.

Cada linha de labeling/rotulos.txt:  <número da linha> <sentimento><tema> [nota]
  + positivo | 0 neutro | - negativo
  e entrega | q qualidade_produto | p preco | a atendimento | d anuncio_divergente | o outro
Exemplo:  7 -d hesitei com o outro

O número é a posição da avaliação no CSV (1 = primeira linha de dados). Pode rodar
de novo a qualquer momento: ele sobrescreve só as linhas citadas em rotulos.txt.
Não mexe em stars_hidden.csv.
"""
import argparse, re, sys
from pathlib import Path

import pandas as pd

SENT = {"+": "positivo", "0": "neutro", "-": "negativo"}
TEMA = {"e": "entrega", "q": "qualidade_produto", "p": "preco",
        "a": "atendimento", "d": "anuncio_divergente", "o": "outro"}
LINHA = re.compile(r"^(\d+)\s+([+\-0])([eqpado])(?:\s+(.*))?$")


def main():
    base = Path(__file__).parent / "labeling"
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rotulos", default=str(base / "rotulos.txt"))
    ap.add_argument("--csv", default=str(base / "to_label.csv"))
    a = ap.parse_args()

    df = pd.read_csv(a.csv, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    for c in ("sentimento", "tema", "nota"):
        if c not in df.columns:
            sys.exit(f"O CSV não tem a coluna '{c}'. Colunas: {list(df.columns)}")

    novos, erros, vistos = {}, [], set()
    for i, linha in enumerate(Path(a.rotulos).read_text(encoding="utf-8").splitlines(), 1):
        t = linha.strip().lower()
        if not t or t.startswith("#"):
            continue
        m = LINHA.match(t)
        if not m:
            erros.append(f"linha {i} do rotulos.txt não entendi: {linha!r}")
            continue
        n = int(m.group(1))
        if not 1 <= n <= len(df):
            erros.append(f"linha {i}: número {n} fora de 1..{len(df)}")
        elif n in vistos:
            erros.append(f"linha {i}: avaliação {n} aparece duas vezes")
        else:
            vistos.add(n)
            novos[n] = (SENT[m.group(2)], TEMA[m.group(3)], (m.group(4) or "").strip())
    if erros:
        print("Nada foi gravado. Corrija:")
        print("\n".join("  " + e for e in erros))
        sys.exit(1)

    for n, (s, t, nota) in novos.items():
        df.loc[n - 1, ["sentimento", "tema"]] = [s, t]
        if nota:
            df.loc[n - 1, "nota"] = nota
    df.to_csv(a.csv, index=False, encoding="utf-8")

    feitos = int(((df["sentimento"] != "") & (df["tema"] != "")).sum())
    print(f"{len(novos)} linhas aplicadas. Rotuladas no total: {feitos}/{len(df)}")


if __name__ == "__main__":
    main()