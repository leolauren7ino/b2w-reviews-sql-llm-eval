# Guia de rotulagem (leia antes de começar, e não mude no meio)

Abra `to_label.csv` e preencha `sentimento` e `tema` para as 200 linhas. Coluna `nota` é livre:
anote ali toda vez que hesitar. Essas hesitações são a melhor matéria-prima da análise de erros.

**Regras fixas (escreva aqui qualquer regra nova que criar e a data):**
- `sentimento` é o do texto como um todo, não da nota. Elogia o produto mas reclama da entrega e
  termina insatisfeito → `negativo`. Mistura equilibrada, sem conclusão clara → `neutro`.
- `tema` é o assunto PRINCIPAL (o que motivou a pessoa a escrever). Um só.
- `anuncio_divergente`: veio outro produto/cor/modelo, faltou item, descrição não bate com o que chegou.
- Sarcasmo vale pelo sentido, não pelas palavras.
- Valores aceitos: sentimento = positivo | neutro | negativo; tema = entrega | qualidade_produto | preco | atendimento | anuncio_divergente | outro.

**Boas práticas**
1. Rotule sem olhar o resultado de nenhum modelo, e as estrelas já estão escondidas de propósito.
2. Faça em 3–4 sessões. Depois de uma semana, re-rotule 30 itens sem olhar suas respostas:
   a taxa de discordância com você mesmo é o teto realista de acurácia do seu gabarito.
3. Termine com `python split.py`; ele valida os valores e divide dev/test. Só rode uma vez.
