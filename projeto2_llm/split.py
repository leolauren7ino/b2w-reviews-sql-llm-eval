"""Depois de rotular: valida o CSV, divide em dev/test (estratificado por sentimento,
seed fixa) e carrega o gabarito no Postgres. Rode UMA vez; o split não muda depois."""
import sys
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from common.db import connect
from schema import SENTIMENTOS, TEMAS

df = pd.read_csv(ROOT / "labeling/to_label.csv")
stars = pd.read_csv(ROOT / "labeling/stars_hidden.csv")
bad_s = ~df.sentimento.isin(SENTIMENTOS); bad_t = ~df.tema.isin(TEMAS)
if bad_s.any() or bad_t.any():
    sys.exit(f"Rótulos faltando/inválidos: {int(bad_s.sum())} sentimentos, {int(bad_t.sum())} temas. "
             f"Valores aceitos: {SENTIMENTOS} / {TEMAS}")
df = df.merge(stars, on="review_id")
dev, test = train_test_split(df, test_size=0.5, stratify=df.sentimento, random_state=42)
df["split"] = df.review_id.map({**{i: "dev" for i in dev.review_id}, **{i: "test" for i in test.review_id}})
with connect() as c, c.cursor() as cur:
    cur.execute((ROOT / "sql/schema.sql").read_text())
    cur.execute("SELECT count(*) FROM gold")
    if cur.fetchone()[0]:
        sys.exit("gold já carregado. Não refaça o split: ele precisa ser fixo.")
    for r in df.itertuples():
        cur.execute("INSERT INTO gold VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (int(r.review_id), r.review_text, len(r.review_text), r.sentimento, r.tema, r.split, int(r.stars)))
print(df.groupby(["split", "sentimento"]).size().unstack(fill_value=0))
