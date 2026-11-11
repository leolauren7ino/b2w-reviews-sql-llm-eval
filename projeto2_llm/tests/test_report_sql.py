"""Exercita schema, fatias SQL e report.py num banco TEMPORÁRIO com dados sintéticos
(só para testar o código; nada disso vai para o banco real nem para o README)."""
import os, subprocess, sys
from pathlib import Path
import psycopg2, pytest

ROOT = Path(__file__).resolve().parent.parent
DB = "portfolio_test"

@pytest.fixture
def tmpdb():
    kw = dict(host=os.getenv("PGHOST", "/tmp"), port=int(os.getenv("PGPORT", "5433")), user=os.getenv("PGUSER", "postgres"))
    try:
        adm = psycopg2.connect(dbname="postgres", **kw); adm.autocommit = True
    except psycopg2.OperationalError:
        pytest.skip("Postgres indisponível")
    cur = adm.cursor(); cur.execute(f"DROP DATABASE IF EXISTS {DB}"); cur.execute(f"CREATE DATABASE {DB}")
    c = psycopg2.connect(dbname=DB, **kw); c.autocommit = True
    k = c.cursor(); k.execute((ROOT / "sql/schema.sql").read_text())
    S = ["positivo", "neutro", "negativo"]
    for i in range(12):
        k.execute("INSERT INTO gold VALUES (%s,%s,%s,%s,%s,%s,%s)", (i, "t" * (20 + i * 30), 20 + i * 30, S[i % 3], "entrega", "dev", 1 + i % 5))
    for run in range(2):
        k.execute("INSERT INTO runs (prompt_version, model, split, run_idx) VALUES ('vT','m','dev',%s) RETURNING run_id", (run,))
        rid = k.fetchone()[0]
        for i in range(12):
            wrong = (i == 3) or (i == 4 and run == 1)
            valid = i != 7
            k.execute("INSERT INTO predictions VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                      (rid, i, ("negativo" if wrong else S[i % 3]) if valid else None, "entrega" if valid else None,
                       valid, 1 if valid else 3, None if valid else "json_quebrado", "{}", 10))
    c.close(); adm.close()
    yield kw
    adm = psycopg2.connect(dbname="postgres", **kw); adm.autocommit = True
    adm.cursor().execute(f"DROP DATABASE IF EXISTS {DB}"); adm.close()

def test_report_roda_e_conta_erros(tmpdb, tmp_path):
    env = {**os.environ, "PGDATABASE": DB}
    r = subprocess.run([sys.executable, "report.py", "--prompt", "vT", "--split", "dev"], cwd=ROOT, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    rep = (ROOT / "reports/vT_dev.md").read_text()
    assert "instabilidade_entre_execucoes" in rep and "respostas_quebradas" in rep
    errs = (ROOT / "reports/vT_dev_erros.csv").read_text()
    assert errs.count("\n") >= 4   # itens 3, 4, 7 + cabeçalho
    (ROOT / "reports/vT_dev.md").unlink(); (ROOT / "reports/vT_dev_erros.csv").unlink()
