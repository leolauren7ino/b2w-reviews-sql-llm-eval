"""Roda um prompt sobre um split, N vezes, grava tudo no Postgres e imprime métricas.

  python run_eval.py --prompt v1 --split dev --runs 3
  python run_eval.py --prompt v2 --split test --runs 3 --final   # única vez por versão

O split 'test' só roda com --final e no máximo uma vez por versão de prompt:
cada olhada no teste enquanto se ajusta o prompt o transforma em dev.
"""
import argparse, logging, sys
from concurrent.futures import ThreadPoolExecutor
import anthropic
from common_path import setup  # noqa: F401  (ajusta sys.path)
from common.db import connect
from llm import classify, DEFAULT_MODEL
from prompts import PROMPTS

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True, choices=PROMPTS)
    ap.add_argument("--split", required=True, choices=["dev", "test"])
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--final", action="store_true", help="obrigatório para o split test")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, filename="run_eval.log",
                        format="%(asctime)s %(levelname)s %(message)s")

    with connect() as conn:
        cur = conn.cursor()
        if a.split == "test":
            if not a.final:
                sys.exit("O split test exige --final.")
            cur.execute("SELECT count(*) FROM runs WHERE split='test' AND prompt_version=%s", (a.prompt,))
            if cur.fetchone()[0]:
                sys.exit(f"{a.prompt} já foi avaliado no test. Crie uma nova versão de prompt.")
        cur.execute("SELECT review_id, review_text, sentimento, tema FROM gold WHERE split=%s ORDER BY review_id", (a.split,))
        items = cur.fetchall()
        if not items:
            sys.exit("Sem gabarito carregado: rode prepare_sample.py, rotule, depois split.py.")
        client = anthropic.Anthropic()
        system = PROMPTS[a.prompt]
        for run_idx in range(a.runs):
            cur.execute("INSERT INTO runs (prompt_version, model, split, run_idx) VALUES (%s,%s,%s,%s) RETURNING run_id",
                        (a.prompt, a.model, a.split, run_idx))
            run_id = cur.fetchone()[0]
            with ThreadPoolExecutor(a.workers) as ex:
                results = list(ex.map(lambda it: classify(client, it[1], system, a.model), items))
            for it, r in zip(items, results):
                p = r.prediction
                cur.execute("INSERT INTO predictions VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            (run_id, it[0], p and p.sentimento, p and p.tema, r.valid, r.attempts, r.error, r.raw, r.latency_ms))
            conn.commit()
            print(f"run {run_idx}: {sum(r.valid for r in results)}/{len(results)} respostas válidas")
    print("Métricas: python report.py --prompt", a.prompt, "--split", a.split)

if __name__ == "__main__":
    main()
