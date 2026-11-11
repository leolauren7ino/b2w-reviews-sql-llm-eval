"""Roda as queries de queries/*.sql e grava os resultados em RESULTADOS.md."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from common.db import connect

out = ["# Resultados das 10 perguntas\n"]
with connect() as conn, conn.cursor() as cur:
    for f in sorted((Path(__file__).parent / "queries").glob("q*.sql")):
        sql = f.read_text()
        title = sql.splitlines()[0].removeprefix("-- ").strip()
        cur.execute(sql)
        cols = [c.name for c in cur.description]
        rows = cur.fetchall()
        out.append(f"## {title}\n\n```sql\n{sql.strip()}\n```\n")
        out.append("| " + " | ".join(cols) + " |")
        out.append("|" + "---|" * len(cols))
        for r in rows[:40]:
            out.append("| " + " | ".join(str(x) for x in r) + " |")
        out.append("")
        print(f.name, len(rows), "linhas")
(Path(__file__).parent / "RESULTADOS.md").write_text("\n".join(out))
