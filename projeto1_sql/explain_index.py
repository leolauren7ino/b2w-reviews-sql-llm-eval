"""EXPLAIN ANALYZE antes e depois de criar índices. Resultado em EXPLAIN.md.
Cada consulta roda 1 vez para aquecer o cache e a segunda é a registrada."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from common.db import connect

def _cliente_recorrente():
    with connect() as c, c.cursor() as cur:
        cur.execute("SELECT reviewer_id FROM reviews GROUP BY reviewer_id HAVING count(*) > 5 ORDER BY reviewer_id LIMIT 1")
        return cur.fetchone()[0]

# literal fixo: um subselect para achar o cliente também usaria o índice e poluiria a comparação
CLIENTE = _cliente_recorrente()

EXPERIMENTOS = [
    ("Histórico de um cliente (filtro por reviewer_id)",
     "SELECT review_id, product_id, rating, submitted_at FROM reviews "
     f"WHERE reviewer_id = '{CLIENTE}' ORDER BY submitted_at",
     "CREATE INDEX idx_reviews_reviewer ON reviews (reviewer_id, submitted_at)"),
    ("Avaliações recentes de um produto (product_id + ordenação por data)",
     "SELECT review_id, rating, submitted_at FROM reviews "
     "WHERE product_id = 132532965 ORDER BY submitted_at DESC LIMIT 20",
     "CREATE INDEX idx_reviews_product_date ON reviews (product_id, submitted_at DESC)"),
]

def explain(cur, sql):
    cur.execute("EXPLAIN (ANALYZE, BUFFERS) " + sql)
    cur.execute("EXPLAIN (ANALYZE, BUFFERS) " + sql)  # 2ª execução = cache quente
    return "\n".join(r[0] for r in cur.fetchall())

out = ["# EXPLAIN antes e depois do índice\n"]
with connect() as conn:
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DROP INDEX IF EXISTS idx_reviews_reviewer, idx_reviews_product_date")
    cur.execute("ANALYZE reviews")
    for titulo, sql, ddl in EXPERIMENTOS:
        antes = explain(cur, sql)
        cur.execute(ddl); cur.execute("ANALYZE reviews")
        depois = explain(cur, sql)
        out += [f"## {titulo}\n", f"```sql\n{sql}\n```\n", f"Índice criado: `{ddl}`\n",
                f"### Antes\n```\n{antes}\n```\n", f"### Depois\n```\n{depois}\n```\n"]
        print(titulo); print([l for l in antes.splitlines() if "Execution" in l], [l for l in depois.splitlines() if "Execution" in l])
(Path(__file__).parent / "EXPLAIN.md").write_text("\n".join(out))
