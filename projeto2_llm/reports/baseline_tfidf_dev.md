# Baseline TF-IDF + regressão logística — split `dev`

Treino: 124979 avaliações (rótulo derivado das estrelas, sem o gabarito) · 113086 features · treino em 21.2 s · inferência de 100 itens em 16.1 ms · custo de API: zero.

Acurácia: **0.88** (IC 95% por bootstrap: 0.82 a 0.94) · F1 macro: 0.804

| classe | precision | recall | f1 | support |
|---|---|---|---|---|
| positivo | 0.865 | 0.938 | 0.9 | 48 |
| neutro | 0.571 | 0.667 | 0.615 | 6 |
| negativo | 0.951 | 0.848 | 0.897 | 46 |

Matriz de confusão (linhas = gabarito rotulado por Claude, colunas = previsão do baseline):

| gabarito | positivo | neutro | negativo |
|---|---|---|---|
| positivo | 45 | 3 | 0 |
| neutro | 0 | 4 | 2 |
| negativo | 7 | 0 | 39 |

Atenção: treino por estrelas, avaliação por rótulo de leitura (Claude); ver README do projeto.
