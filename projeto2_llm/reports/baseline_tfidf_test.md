# Baseline TF-IDF + regressão logística — split `test`

Treino: 124979 avaliações (rótulo derivado das estrelas, sem o gabarito) · 113086 features · treino em 21.2 s · inferência de 100 itens em 5.0 ms · custo de API: zero.

Acurácia: **0.84** (IC 95% por bootstrap: 0.77 a 0.91) · F1 macro: 0.715

| classe | precision | recall | f1 | support |
|---|---|---|---|---|
| positivo | 0.865 | 0.957 | 0.909 | 47 |
| neutro | 0.375 | 0.429 | 0.4 | 7 |
| negativo | 0.9 | 0.783 | 0.837 | 46 |

Matriz de confusão (linhas = gabarito rotulado por Claude, colunas = previsão do baseline):

| gabarito | positivo | neutro | negativo |
|---|---|---|---|
| positivo | 45 | 0 | 2 |
| neutro | 2 | 3 | 2 |
| negativo | 5 | 5 | 36 |

Atenção: treino por estrelas, avaliação por rótulo de leitura (Claude); ver README do projeto.
