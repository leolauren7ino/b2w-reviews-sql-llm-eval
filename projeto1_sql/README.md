# Projeto 1 — pandas + PostgreSQL sobre avaliações reais da B2W

Dataset: **B2W-Reviews01**, 132.373 avaliações de produtos (jan–mai/2018), em português.
Fluxo: CSV bruto → limpeza com pandas → `COPY` para Postgres → 10 perguntas em SQL → índice com `EXPLAIN ANALYZE` antes/depois.

```bash
python projeto1_sql/clean_and_load.py   # limpa e carrega (gera cleaning_report.json)
python projeto1_sql/run_queries.py      # roda queries/*.sql  -> RESULTADOS.md
python projeto1_sql/explain_index.py    # -> EXPLAIN.md
```

## Limpeza (cada regra mede o que afetou)
| Regra | Linhas afetadas |
|---|---|
| Linhas brutas | 132.373 |
| Texto vazio → `NULL` | 3.275 |
| Ano de nascimento implausível (<1920 ou >2005; o bruto ia de 59 a 2018) → `NULL` | 108 |
| Duplicatas (mesmo cliente + produto + título + texto; fica a primeira) | 1.298 removidas |
| **Linhas finais no Postgres** | **131.075** |

Normalizar a caixa/espaços da marca não mudou nada (1.062 marcas antes e depois): o dado já vinha limpo
nesse campo. Mantive 4.001 linhas em que nota e "recomenda" se contradizem (nota ≤2 e recomenda, ou ≥4 e
não recomenda): é sinal do dado, não erro a corrigir — ver Q6.

## As 10 perguntas (SQL em `queries/`, resultados completos em `RESULTADOS.md`)
| # | Pergunta | Técnica |
|---|---|---|
| 1 | Volume e nota por mês, com variação | CTE + `LAG` |
| 2 | Top 3 categorias de cada mês | CTE + `RANK() PARTITION BY` |
| 3 | Total acumulado e % do total | `SUM() OVER` |
| 4 | Melhores/piores produtos (≥40 avaliações) | `RANK` vs `DENSE_RANK`, `HAVING` |
| 5 | Quem reavaliou o mesmo produto | `ROW_NUMBER`, deduplicação |
| 6 | "Recomenda" é coerente com a nota? | agregação + `SUM() OVER ()` |
| 7 | Marcas acima da média da categoria | `AVG() OVER PARTITION` |
| 8 | Estados com mais nota 1 | CTE + `RANK` |
| 9 | Texto longo = reclamação? | `CASE` em faixas |
| 10 | Tempo entre avaliações do mesmo cliente | `LAG` + `percentile_cont` |

## O que os dados dizem (e o que não dizem)
- **Texto longo é reclamação.** Nota média 3,88 (textos de 40–99 caracteres) → 2,74 (200+); % de nota 1 sobe de 11,5% para 38,1%. É o achado mais forte, e é o que torna o tamanho do texto uma fatia relevante no Projeto 2.
- **"Recomenda" quase espelha a nota**, com um degrau em 3 estrelas: 98,5% recomendam com nota 5, 88,6% com nota 3, 24,6% com nota 2, 2,9% com nota 1.
- **Marcas acima da média da categoria** (≥100 avaliações): Microsoft e Logitech (+0,5 em Informática e Acessórios), Samsung, Philips Walita, Apple.
- **Estados:** a diferença de % de nota 1 vai de 17,9% (PR) a 23,3% (RJ/PI). São 5 pontos entre os extremos, e PI tem só 686 avaliações; eu **não** tiraria conclusão regional daqui sem teste estatístico.
- **Cuidado com fevereiro:** o volume cai 66% (34.570 → 11.616) e volta em março. Pode ser sazonalidade, mas fevereiro de 2018 não explica uma queda dessas; suspeito de lacuna na coleta do dataset. **Não investiguei**, então não reporto como tendência de negócio.
- Q5: 800 pares cliente×produto com reavaliação (858 reavaliações); nota média cai pouco entre a 1ª e as seguintes (1,76 → 1,86): quem reavalia geralmente já estava insatisfeito.

## Índice: `EXPLAIN (ANALYZE, BUFFERS)` antes e depois (131.075 linhas, cache quente)
| Consulta | Plano antes | Tempo | Índice | Plano depois | Tempo |
|---|---|---|---|---|---|
| Histórico de um cliente (`reviewer_id = …`) | Seq Scan | 22,4 ms | `(reviewer_id, submitted_at)` | Bitmap Index Scan | 0,03 ms |
| 20 últimas avaliações de um produto | Seq Scan | 20,0 ms | `(product_id, submitted_at DESC)` | Bitmap Index Scan | 0,05 ms |

Ordem de grandeza: centenas de vezes mais rápido (de ~380× a ~660× nesta medição). Planos completos em `EXPLAIN.md`.
Ressalvas honestas: são milissegundos numa tabela pequena (a lição é o plano mudar de varredura total para
índice, não o ganho absoluto); medi com uma execução de aquecimento e uma medida, num Postgres 16 em Docker, dentro de um Codespaces (numa máquina local os tempos foram outros, mas o plano antes e depois do índice foi o mesmo);
e o primeiro experimento foi refeito porque um subselect para escolher o cliente também usava o índice e
distorcia a comparação, por isso o `reviewer_id` entra como literal.
