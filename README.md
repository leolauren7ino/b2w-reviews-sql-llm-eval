# Portfólio de dados: SQL e avaliação de LLM sobre avaliações em português

| Projeto | O que prova |
|---|---|
| [`projeto1_sql`](projeto1_sql/README.md) | pandas + PostgreSQL: limpeza medida, CTEs, window functions, deduplicação, `EXPLAIN` antes/depois de índice |
| [`projeto2_llm`](projeto2_llm/README.md) | Classificador com LLM, saída validada, gabarito próprio com split dev/test, inconsistência entre execuções, análise de erros em SQL |

Dataset comum: B2W-Reviews01 (baixado de `huggingface.co/datasets/vladjr/B2W-Reviews01`, fora do git em `data/raw/`).

**Estado:** Projeto 1 completo e executado. Projeto 2 com pipeline construído e testado (11 testes), mas
**aguardando o gabarito manual e uma `ANTHROPIC_API_KEY`**; por isso não há métricas nele ainda.

## Ambiente
Python 3.12+ e Postgres 16. O jeito mais simples é Docker:

```bash
docker run -d --name pg -e POSTGRES_PASSWORD=dev -p 5432:5432 postgres:16
until docker exec pg pg_isready -U postgres; do sleep 1; done
docker exec pg psql -U postgres -c "CREATE DATABASE portfolio;"

export PGHOST=localhost PGPORT=5432 PGUSER=postgres PGPASSWORD=dev PGDATABASE=portfolio
pip install -r requirements.txt
mkdir -p data/raw
curl -L -o data/raw/b2w.csv https://huggingface.co/datasets/vladjr/B2W-Reviews01/resolve/main/B2W-Reviews01.csv
python projeto1_sql/clean_and_load.py
```

Os scripts leem `PGHOST/PGPORT/PGUSER/PGPASSWORD/PGDATABASE`; sem elas, o padrão é socket `/tmp`, porta 5433 e banco `portfolio`. No PowerShell, use `curl.exe` e `$env:PGHOST="localhost"` etc.
