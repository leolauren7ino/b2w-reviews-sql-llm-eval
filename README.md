# Portfólio de dados: SQL e avaliação de LLM sobre avaliações em português

| Projeto | O que prova |
|---|---|
| [`projeto1_sql`](projeto1_sql/README.md) | pandas + PostgreSQL: limpeza medida, CTEs, window functions, deduplicação, `EXPLAIN` antes/depois de índice |
| [`projeto2_llm`](projeto2_llm/README.md) | Classificador com LLM, saída validada, gabarito próprio com split dev/test, inconsistência entre execuções, análise de erros em SQL |

Dataset comum: B2W-Reviews01 (baixado de `huggingface.co/datasets/vladjr/B2W-Reviews01`, fora do git em `data/raw/`).

**Estado:** Projeto 1 completo e executado. Projeto 2 com pipeline construído e testado (11 testes), mas
**aguardando o gabarito manual e uma `ANTHROPIC_API_KEY`**; por isso não há métricas nele ainda.

## Ambiente
Postgres 16 (os scripts leem `PGHOST/PGPORT/PGUSER/PGPASSWORD/PGDATABASE`; padrão: socket `/tmp`, porta 5433, banco `portfolio`).
```bash
pip install -r requirements.txt
mkdir -p data/raw && curl -L -o data/raw/b2w.csv https://huggingface.co/datasets/vladjr/B2W-Reviews01/resolve/main/B2W-Reviews01.csv
```
