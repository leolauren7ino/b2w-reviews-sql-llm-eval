# Relatório — prompt `v1` no split `dev`

Modelo(s): gemini-3.5-flash-lite · execuções: 2 · itens: 100

## sentimento: acurácia por execução

| execucao | acuracia |
|---|---|
| 0 | 0.93 |
| 1 | 0.95 |

Variação entre execuções: 0.93 a 0.95

### sentimento: precisão / recall / F1 por classe (execuções agregadas)

| classe | precision | recall | f1 | support |
|---|---|---|---|---|
| positivo | 0.931 | 0.979 | 0.954 | 96 |
| neutro | 0.5 | 0.25 | 0.333 | 12 |
| negativo | 0.978 | 0.989 | 0.984 | 92 |

### sentimento: matriz de confusão (linhas = gabarito, colunas = previsão)

| gabarito | negativo | neutro | positivo |
|---|---|---|---|
| positivo | 0 | 2 | 94 |
| neutro | 2 | 3 | 7 |
| negativo | 91 | 1 | 0 |

Consistência (sentimento): 2 de 100 itens mudaram de rótulo entre execuções (2.0%).

## tema: acurácia por execução

| execucao | acuracia |
|---|---|
| 0 | 0.83 |
| 1 | 0.83 |

Variação entre execuções: 0.83 a 0.83

### tema: precisão / recall / F1 por classe (execuções agregadas)

| classe | precision | recall | f1 | support |
|---|---|---|---|---|
| entrega | 0.743 | 0.765 | 0.754 | 34 |
| qualidade_produto | 0.957 | 0.854 | 0.902 | 130 |
| preco | 0.571 | 1.0 | 0.727 | 8 |
| atendimento | 0.25 | 0.667 | 0.364 | 6 |
| anuncio_divergente | 0.889 | 0.889 | 0.889 | 18 |
| outro | 1.0 | 0.25 | 0.4 | 4 |

### tema: matriz de confusão (linhas = gabarito, colunas = previsão)

| gabarito | anuncio_divergente | atendimento | entrega | outro | preco | qualidade_produto |
|---|---|---|---|---|---|---|
| entrega | 2 | 4 | 26 | 0 | 0 | 2 |
| qualidade_produto | 0 | 4 | 9 | 0 | 6 | 111 |
| preco | 0 | 0 | 0 | 0 | 8 | 0 |
| atendimento | 0 | 4 | 0 | 0 | 0 | 2 |
| anuncio_divergente | 16 | 2 | 0 | 0 | 0 | 0 |
| outro | 0 | 2 | 0 | 1 | 0 | 1 |

Consistência (tema): 4 de 100 itens mudaram de rótulo entre execuções (4.0%).

## SQL: erro_por_classe_sentimento

| classe_real | n | pct_erro |
|---|---|---|
| neutro | 12 | 75.0 |
| positivo | 96 | 2.1 |
| negativo | 92 | 1.1 |

## SQL: erro_por_classe_tema

| classe_real | n | pct_erro |
|---|---|---|
| outro | 4 | 75.0 |
| atendimento | 6 | 33.3 |
| entrega | 34 | 23.5 |
| qualidade_produto | 130 | 14.6 |
| anuncio_divergente | 18 | 11.1 |
| preco | 8 | 0.0 |

## SQL: erro_por_tamanho_texto

| faixa | n | pct_erro_sentimento | pct_erro_tema |
|---|---|---|---|
| 1) <80 | 64 | 6.3 | 9.4 |
| 2) 80-159 | 82 | 7.3 | 20.7 |
| 3) 160-299 | 40 | 5.0 | 27.5 |
| 4) 300+ | 14 | 0.0 | 0.0 |

## SQL: erro_por_estrelas_originais

| stars | n | pct_erro_sentimento |
|---|---|---|
| 1 | 38 | 5.3 |
| 2 | 42 | 7.1 |
| 3 | 34 | 20.6 |
| 4 | 40 | 0.0 |
| 5 | 46 | 0.0 |

## SQL: instabilidade_entre_execucoes

| rotulos_distintos | itens |
|---|---|
| 1 | 98 |
| 2 | 2 |

## SQL: respostas_quebradas

| total | invalidas | validas_apos_retry | latencia_media_ms |
|---|---|---|---|
| 200 | 0 | 0 | 6967.0 |

## Erros para análise manual

25 itens com erro em ao menos uma execução → `v1_dev_erros.csv`.

Ainda sem causas anotadas (preencha a coluna `causa`).
