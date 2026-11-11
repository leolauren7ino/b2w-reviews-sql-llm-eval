"""Sorteia os textos que VOCÊ vai rotular à mão.

- 40 por faixa de estrelas (1..5) => 200 itens, para a classe 'neutro' e as notas
  extremas não ficarem raras. Consequência: a distribuição NÃO é a natural; as
  métricas valem para este conjunto e o README deve dizer isso.
- O arquivo de rotulagem NÃO traz as estrelas: rotular vendo a nota contamina o gabarito.
Saída: labeling/to_label.csv (preencha sentimento, tema, nota) e labeling/stars_hidden.csv.
"""
import sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from common.db import connect

PER_STAR, SEED = 40, 42
with connect() as c:
    df = pd.read_sql("SELECT review_id, review_text, rating AS stars FROM reviews "
                     "WHERE review_text IS NOT NULL AND length(review_text) BETWEEN 30 AND 600", c)
amostra = (df.groupby("stars").sample(PER_STAR, random_state=SEED)
             .sample(frac=1, random_state=SEED).reset_index(drop=True))
out = ROOT / "labeling"
out.mkdir(exist_ok=True)
amostra[["review_id", "review_text"]].assign(sentimento="", tema="", nota="").to_csv(out / "to_label.csv", index=False)
amostra[["review_id", "stars"]].to_csv(out / "stars_hidden.csv", index=False)
print(f"{len(amostra)} itens em labeling/to_label.csv")
