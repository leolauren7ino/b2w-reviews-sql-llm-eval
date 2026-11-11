"""Projeto 1 — limpa o B2W-Reviews01 com pandas e carrega no Postgres.

Uso:  python projeto1_sql/clean_and_load.py
Cada regra de limpeza registra quantas linhas afetou; o resumo vai para
projeto1_sql/cleaning_report.json e é citado no README.
"""
import io, json, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from common.db import connect  # noqa: E402

RAW = ROOT / "data/raw/b2w.csv"
REPORT = Path(__file__).parent / "cleaning_report.json"

DDL = """
DROP TABLE IF EXISTS reviews CASCADE;
CREATE TABLE reviews (
    review_id      BIGSERIAL PRIMARY KEY,
    submitted_at   TIMESTAMP NOT NULL,
    reviewer_id    TEXT NOT NULL,
    product_id     BIGINT NOT NULL,
    product_name   TEXT,
    brand          TEXT,
    category_lv1   TEXT,
    category_lv2   TEXT,
    title          TEXT,
    rating         SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    recommends     BOOLEAN,
    review_text    TEXT,
    birth_year     SMALLINT,
    gender         CHAR(1),
    state          CHAR(2)
);
"""

def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    log = {"linhas_brutas": len(df)}

    df = df.rename(columns={
        "submission_date": "submitted_at", "product_brand": "brand",
        "site_category_lv1": "category_lv1", "site_category_lv2": "category_lv2",
        "review_title": "title", "overall_rating": "rating",
        "recommend_to_a_friend": "recommends", "reviewer_birth_year": "birth_year",
        "reviewer_gender": "gender", "reviewer_state": "state",
    })

    # 1) texto: espaços repetidos / quebras de linha; vazio vira NULL
    for col in ["review_text", "title", "product_name", "category_lv1", "category_lv2"]:
        df[col] = df[col].astype("string").str.replace(r"\s+", " ", regex=True).str.strip()
    vazios = df["review_text"].fillna("").eq("")
    log["texto_vazio_virou_null"] = int(vazios.sum())
    df.loc[vazios, "review_text"] = pd.NA

    # 2) marca: 69% nula; o resto vem com caixa/espaços inconsistentes
    df["brand"] = df["brand"].astype("string").str.strip().str.lower()
    log["marcas_distintas_antes_depois"] = [
        int(pd.read_csv(RAW, usecols=["product_brand"]).product_brand.nunique()),
        int(df["brand"].nunique()),
    ]

    # 3) tipos
    df["submitted_at"] = pd.to_datetime(df["submitted_at"], errors="coerce")
    log["datas_invalidas_removidas"] = int(df["submitted_at"].isna().sum())
    df = df.dropna(subset=["submitted_at"])
    df["recommends"] = df["recommends"].map({"Yes": True, "No": False}).astype("boolean")

    # 4) ano de nascimento implausível (min=59, max=2018 no bruto)
    ruim = df["birth_year"].notna() & ~df["birth_year"].between(1920, 2005)
    log["ano_nascimento_implausivel_virou_null"] = int(ruim.sum())
    df.loc[ruim, "birth_year"] = pd.NA
    df["birth_year"] = df["birth_year"].astype("Int16")

    # 5) deduplicação: mesma pessoa, mesmo produto, mesmo texto => fica a primeira
    antes = len(df)
    df = df.sort_values("submitted_at")
    chave = ["reviewer_id", "product_id", "review_text", "title"]
    df = df.drop_duplicates(subset=chave, keep="first")
    log["duplicatas_removidas"] = antes - len(df)

    # 6) coerência rating x recomendação (não corrijo; só meço)
    incoerente = ((df["rating"] <= 2) & (df["recommends"] == True)) | \
                 ((df["rating"] >= 4) & (df["recommends"] == False))
    log["rating_vs_recomenda_incoerentes_mantidos"] = int(incoerente.sum())

    log["linhas_finais"] = len(df)
    return df.reset_index(drop=True), log

def main():
    df = pd.read_csv(RAW, low_memory=False)
    df, log = clean(df)
    cols = ["submitted_at", "reviewer_id", "product_id", "product_name", "brand",
            "category_lv1", "category_lv2", "title", "rating", "recommends",
            "review_text", "birth_year", "gender", "state"]
    buf = io.StringIO()
    df[cols].to_csv(buf, index=False, header=False)
    buf.seek(0)
    with connect() as conn, conn.cursor() as cur:
        cur.execute(DDL)
        cur.copy_expert(f"COPY reviews ({','.join(cols)}) FROM STDIN WITH CSV", buf)
        cur.execute("SELECT count(*) FROM reviews")
        log["linhas_no_postgres"] = cur.fetchone()[0]
    REPORT.write_text(json.dumps(log, indent=2, ensure_ascii=False))
    print(json.dumps(log, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
