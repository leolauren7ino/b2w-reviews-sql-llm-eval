# Relatório — prompt `v1` no split `test`

Modelo(s): gemini-3.5-flash-lite · execuções: 2 · itens: 100

## sentimento: acurácia por execução

| execucao | acuracia |
|---|---|
| 0 | 0.95 |
| 1 | 0.96 |

Variação entre execuções: 0.95 a 0.96

### sentimento: precisão / recall / F1 por classe (execuções agregadas)

| classe | precision | recall | f1 | support |
|---|---|---|---|---|
| positivo | 0.969 | 1.0 | 0.984 | 94 |
| neutro | 0.857 | 0.429 | 0.571 | 14 |
| negativo | 0.948 | 0.989 | 0.968 | 92 |

### sentimento: matriz de confusão (linhas = gabarito, colunas = previsão)

| gabarito | negativo | neutro | positivo |
|---|---|---|---|
| positivo | 0 | 0 | 94 |
| neutro | 5 | 6 | 3 |
| negativo | 91 | 1 | 0 |

Consistência (sentimento): 3 de 100 itens mudaram de rótulo entre execuções (3.0%).

## tema: acurácia por execução

| execucao | acuracia |
|---|---|
| 0 | 0.83 |
| 1 | 0.83 |

Variação entre execuções: 0.83 a 0.83

### tema: precisão / recall / F1 por classe (execuções agregadas)

| classe | precision | recall | f1 | support |
|---|---|---|---|---|
| entrega | 0.871 | 0.964 | 0.915 | 28 |
| qualidade_produto | 0.949 | 0.867 | 0.906 | 128 |
| preco | 0.333 | 1.0 | 0.5 | 4 |
| atendimento | 0.077 | 0.25 | 0.118 | 4 |
| anuncio_divergente | 0.846 | 0.846 | 0.846 | 26 |
| outro | 1.0 | 0.1 | 0.182 | 10 |

### tema: matriz de confusão (linhas = gabarito, colunas = previsão)

| gabarito | anuncio_divergente | atendimento | entrega | outro | preco | qualidade_produto |
|---|---|---|---|---|---|---|
| entrega | 0 | 0 | 27 | 0 | 0 | 1 |
| qualidade_produto | 2 | 6 | 1 | 0 | 8 | 111 |
| preco | 0 | 0 | 0 | 0 | 4 | 0 |
| atendimento | 0 | 1 | 1 | 0 | 0 | 2 |
| anuncio_divergente | 22 | 2 | 0 | 0 | 0 | 2 |
| outro | 2 | 4 | 2 | 1 | 0 | 1 |

Consistência (tema): 7 de 100 itens mudaram de rótulo entre execuções (7.0%).

## SQL: erro_por_classe_sentimento

| classe_real | n | pct_erro |
|---|---|---|
| neutro | 14 | 57.1 |
| negativo | 92 | 1.1 |
| positivo | 94 | 0.0 |

## SQL: erro_por_classe_tema

| classe_real | n | pct_erro |
|---|---|---|
| outro | 10 | 90.0 |
| atendimento | 4 | 75.0 |
| anuncio_divergente | 26 | 15.4 |
| qualidade_produto | 128 | 13.3 |
| entrega | 28 | 3.6 |
| preco | 4 | 0.0 |

## SQL: erro_por_tamanho_texto

| faixa | n | pct_erro_sentimento | pct_erro_tema |
|---|---|---|---|
| 1) <80 | 68 | 5.9 | 7.4 |
| 2) 80-159 | 74 | 0.0 | 12.2 |
| 3) 160-299 | 34 | 2.9 | 32.4 |
| 4) 300+ | 24 | 16.7 | 37.5 |

## SQL: erro_por_estrelas_originais

| stars | n | pct_erro_sentimento |
|---|---|---|
| 1 | 42 | 4.8 |
| 2 | 38 | 2.6 |
| 3 | 46 | 6.5 |
| 4 | 40 | 2.5 |
| 5 | 34 | 5.9 |

## SQL: instabilidade_entre_execucoes

| rotulos_distintos | itens |
|---|---|
| 1 | 97 |
| 2 | 3 |

## SQL: respostas_quebradas

| total | invalidas | validas_apos_retry | latencia_media_ms |
|---|---|---|---|
| 200 | 0 | 0 | 6980.0 |

## Erros para análise manual

24 itens com erro em ao menos uma execução → `v1_test_erros.csv`.

Ainda sem causas anotadas (preencha a coluna `causa`).
