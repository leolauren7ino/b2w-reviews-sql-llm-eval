# Data portfolio: SQL and LLM evaluation on Portuguese product reviews

**English summary.** Two projects on the public B2W-Reviews01 dataset (~132k Brazilian e-commerce reviews):
(1) pandas + PostgreSQL: measured data cleaning, CTEs, window functions, deduplication and `EXPLAIN` before/after an index;
(2) an LLM sentiment/topic classifier evaluated honestly: validated structured output, a 200-item gold set with a fixed
dev/test split, run-to-run inconsistency, SQL-based error analysis, and a classical scikit-learn baseline
(TF-IDF + logistic regression) to answer *when does the LLM justify its cost?*
Caveat stated up front: the gold labels were written by Claude (not a human) and the LLM under test is Gemini, so agreement
may overstate agreement with human judgment. Docs below are in Portuguese. Quick start: `docker compose up -d`, then see "Ambiente".

---


| Projeto | O que prova |
|---|---|
| [`projeto1_sql`](projeto1_sql/README.md) | pandas + PostgreSQL: limpeza medida, CTEs, window functions, deduplicação, `EXPLAIN` antes/depois de índice |
| [`projeto2_llm`](projeto2_llm/README.md) | Classificador com LLM, saída validada, gabarito de 200 itens com split dev/test, inconsistência entre execuções, análise de erros em SQL, baseline scikit-learn (TF-IDF + regressão logística) para comparar custo e acurácia |

Dataset comum: B2W-Reviews01 (baixado de `huggingface.co/datasets/vladjr/B2W-Reviews01`, fora do git em `data/raw/`).

**Estado:** Projeto 1 e Projeto 2 completos e executados. No Projeto 2, o gabarito de 200 avaliações foi rotulado por Claude (não por humano) e o classificador (Gemini) foi avaliado em dev e teste com o prompt v1; números e limitações estão no README do projeto.

## Ambiente
Python 3.12+ e Postgres 16. O jeito mais simples é Docker (`docker-compose.yml` já cria o banco `portfolio`):

```bash
docker compose up -d --wait

export PGHOST=localhost PGPORT=5432 PGUSER=postgres PGPASSWORD=dev PGDATABASE=portfolio
pip install -r requirements.txt
mkdir -p data/raw
curl -L -o data/raw/b2w.csv https://huggingface.co/datasets/vladjr/B2W-Reviews01/resolve/main/B2W-Reviews01.csv
python projeto1_sql/clean_and_load.py
```

Os scripts leem `PGHOST/PGPORT/PGUSER/PGPASSWORD/PGDATABASE`; sem elas, o padrão é socket `/tmp`, porta 5433 e banco `portfolio`. No PowerShell, use `curl.exe` e `$env:PGHOST="localhost"` etc.
