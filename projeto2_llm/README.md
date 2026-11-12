# Projeto 2 — Classificador de avaliações com LLM e avaliação honesta

*English summary: LLM sentiment/topic classifier (Gemini free tier) evaluated on a 200-item gold set labeled by Claude, fixed dev/test split, validated JSON output, run-to-run consistency, SQL error analysis, plus a TF-IDF + logistic regression baseline (scikit-learn) on the same test items. Details below in Portuguese.*

> **Estado:** pipeline executado de ponta a ponta (dev e teste, prompt v1, Gemini no plano gratuito).
> O gabarito foi rotulado por Claude (Anthropic), não por humano: veja "Limitações".

## A pergunta
Dá para confiar num LLM para classificar avaliações em português por **sentimento** e **tema**?
Quanto, onde ele erra, e o quanto o resultado muda de uma execução para outra?

## Dados
B2W-Reviews01 (avaliações reais do e-commerce brasileiro, ~132 mil linhas), já limpo no Projeto 1.
Gabarito: **200 avaliações rotuladas por Claude (Anthropic), sem acesso à nota em estrelas** (40 por estrela,
então a distribuição *não* é a natural — as métricas valem para este conjunto).
Divisão fixa (seed 42), estratificada por sentimento: **100 dev** (para ajustar o prompt) e
**100 test** (usado uma única vez por versão final de prompt; o código recusa uma segunda).

## Pipeline
`prepare_sample.py` → *(rotulagem por Claude)* → `split.py` → `run_eval.py` → `report.py`

- Saída do modelo em JSON, validada com pydantic (`schema.py`, sem campos extras, valores só da taxonomia).
- `llm.py` trata JSON quebrado/envolto em prosa, valores fora da taxonomia, `refusal`/`max_tokens` e erros
  de API: retry de até 3 tentativas devolvendo o erro ao modelo; tudo logado. Resposta que nunca fica
  válida **conta como erro** (não é descartada, senão a acurácia infla).
- Tudo vai para o Postgres (`gold`, `runs`, `predictions`, com a resposta bruta) e as fatias de erro
  são SQL (`sql/slices.sql`).
- Observação técnica: os modelos atuais da API não aceitam `temperature`; a variação entre execuções
  é a do amostrador padrão. Usei `effort: low`, adequado a classificação.

## Provedor de LLM
O `llm.py` usa o formato do SDK da Anthropic. Para trocar de provedor sem mexer nele, o `compat_client.py`
adapta qualquer endpoint compatível com a API da OpenAI (Gemini, Ollama etc.), e o `run_eval.py` escolhe o
cliente pela variável `LLM_PROVIDER` (padrão: Anthropic).

Gemini, no plano gratuito do Google AI Studio:
```bash
export LLM_PROVIDER=gemini LLM_API_KEY=... LLM_MIN_INTERVAL=7
export LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
python run_eval.py --prompt v1 --split dev --runs 3 --model gemini-3.5-flash-lite --workers 1
```

- `LLM_MIN_INTERVAL` espaça as chamadas para não estourar o limite por minuto: um erro 429 contaria como
  resposta inválida e distorceria a acurácia. Por isso a latência registrada **inclui essa espera** e não
  deve ser lida como latência do modelo.
- Use sempre um nome de modelo versionado (não um apelido `-latest`) e registre-o junto das métricas.
- O parâmetro `effort` é específico da Anthropic e é ignorado nos outros provedores.

## Resultados
Modelo `gemini-3.5-flash-lite` (plano gratuito), prompt `v1`, 2 execuções por conjunto.
O prompt não foi alterado entre dev e teste.

| | dev | teste |
|---|---|---|
| Acurácia, sentimento | 0,93 e 0,95 | 0,95 e 0,96 |
| Acurácia, tema | 0,83 e 0,83 | 0,83 e 0,83 |
| Itens que mudaram entre execuções (sentimento / tema) | 2 / 4 de 100 | 3 / 7 de 100 |
| Respostas inválidas | 0 de 200 | 0 de 200 |

Métricas por classe no teste (execuções agregadas; `support` conta item × execução, então são 2 por item):

**Sentimento**

| classe | precision | recall | f1 | support |
|---|---|---|---|---|
| positivo | 0,969 | 1,000 | 0,984 | 94 |
| neutro | 0,857 | 0,429 | 0,571 | 14 |
| negativo | 0,948 | 0,989 | 0,968 | 92 |

**Tema**

| classe | precision | recall | f1 | support |
|---|---|---|---|---|
| entrega | 0,871 | 0,964 | 0,915 | 28 |
| qualidade_produto | 0,949 | 0,867 | 0,906 | 128 |
| preco | 0,333 | 1,000 | 0,500 | 4 |
| atendimento | 0,077 | 0,250 | 0,118 | 4 |
| anuncio_divergente | 0,846 | 0,846 | 0,846 | 26 |
| outro | 1,000 | 0,100 | 0,182 | 10 |

Leitura: positivo e negativo são sólidos. `neutro` (7 itens no teste) e as classes de tema com
2 a 5 itens (preco, atendimento, outro) não sustentam conclusão. A latência registrada inclui a
espera de 7 s entre chamadas e não é a do modelo.

## Análise de erros
Os 25 erros do dev (`reports/v1_dev_erros.csv`) foram lidos e classificados. A classificação foi
feita por Claude, o mesmo que rotulou o gabarito, e deve ser conferida pelo autor.
Em 24 dos 25 erros, o rótulo tinha nota de hesitação registrada antes da avaliação
(hesitação em 55% das 200 avaliações).

| Causa | Itens | Exemplo real |
|---|---|---|
| Ambiguidade genuína (texto com dois assuntos, ou fronteira do neutro) | 23 | "Produto chegou antes do tempo previsto, embalagem perfeita e produto de ótima qualidade." Rotulado qualidade, previsto entrega |
| Viés/limitação do modelo | 1 | "Produto chegou com defeito tive que pedir troca mandei de volta..." Rotulado entrega, previsto atendimento (a confirmar) |
| Rótulo do gabarito errado | 1 | "Achei o produto bonito quando vir na foto quando chegou era deferente da foto mais td bem fez a devolução..." Rotulado negativo, previsto neutro em uma execução |
| Instrução ruim no prompt | 0 | O prompt não traz regra de desempate para textos com vários assuntos; não foi alterado |

Os 24 itens com erro do teste não foram analisados, porque o prompt já estava congelado.

## O que mudei no prompt e o efeito
Nada: o v1 foi mantido (ver `prompts/CHANGELOG.md`). Os erros do dev não mostraram um padrão que um
prompt corrija; a minha própria regra de desempate entre temas não foi consistente, e uma v2
estaria ajustando o prompt ao ruído do gabarito.
Teste final (uma vez): sentimento 0,95 e 0,96; tema 0,83 e 0,83. Diferença dev vs teste: +0,02 em
sentimento e 0,00 em tema, sem sinal de ajuste ao dev, já que o prompt não foi ajustado.

## Baseline clássico (scikit-learn) e a escolha de modelo
Para responder "o LLM compensa?", `baseline_tfidf.py` treina TF-IDF (1-2 gramas) + regressão logística e avalia nos **mesmos
itens de dev e teste** do LLM. Sem API, sem Postgres:

```bash
python baseline_tfidf.py --raw ../data/raw/b2w.csv    # gera reports/baseline_tfidf_dev.md e _test.md
```

Como o experimento foi desenhado (e o que ele não permite concluir):
- **Treino:** avaliações do B2W com rótulo derivado das estrelas (1-2 negativo, 3 neutro, 4-5 positivo), excluindo os 200
  itens do gabarito e textos idênticos a eles. Hiperparâmetros fixos, definidos antes de ver dev/teste.
- **Critérios diferentes:** o baseline aprende "o que a nota diz"; o gabarito foi rotulado por Claude lendo o texto, sem ver a nota.
  Parte do erro do baseline é discordância entre nota e texto (um 3 estrelas que o texto lê como negativo), não falha de modelo.
  A comparação com o LLM é, portanto, entre modelos avaliados no mesmo teste, mas treinados/instruídos por critérios distintos.
- **Só sentimento:** o tema existe apenas no gabarito de 200 itens, pequeno demais para treinar um modelo.
- **Incerteza:** com 100 itens de teste, o relatório traz IC 95% por bootstrap; diferenças menores que a largura do intervalo são ruído.
- **Custo:** o relatório registra tempo de treino e de inferência; o baseline não tem custo de API nem limite de requisições.

### Resultado: baseline x LLM no mesmo teste (100 itens, sentimento)

| | TF-IDF + reg. logística | Gemini (prompt v1, 2 execuções) |
|---|---|---|
| Acurácia | 0,84 (IC 95%: 0,77 a 0,91) | 0,95 e 0,96 |
| F1 macro | 0,715 | 0,84 |
| Recall `negativo` | 0,78 (36 de 46) | 0,99 |
| Recall `neutro` | 0,43 (3 de 7) | 0,43 |
| Custo | treino 21 s, inferência 5 ms por 100 itens, sem API | chamadas de API no plano gratuito, ~7 s por item (inclui espera do limite de taxa) |

Leitura, com o que os dados sustentam:
- O LLM ficou acima do limite superior do intervalo do baseline (0,91). A diferença provavelmente é real, mas a comparação
  é aproximada: o intervalo é só do baseline, e um teste pareado (McNemar) exigiria as previsões do LLM por item.
- A diferença vem do `negativo`: o baseline errou 10 avaliações negativas (5 para positivo, 5 para neutro). No `neutro`
  os dois empatam, mas com 7 itens isso não permite conclusão.
- Parte da diferença é de critério, não de capacidade: o baseline aprendeu com estrelas e o gabarito é uma leitura do texto
  feita por Claude. Um LLM tende a concordar mais com outro LLM do que com uma nota. Não sei quanto da diferença é isso.
- Os 10 erros em `negativo` foram lidos (abaixo): 6 são falha real do modelo e 4 são discordância entre nota e texto.
- Se o objetivo é separar positivo de negativo a custo zero e com latência de milissegundos, o baseline já chega a 0,84
  e roda sem API nem limite de requisições. O LLM compensa quando o erro em `negativo` é caro (reclamações que passam
  despercebidas), com o custo de depender de uma API e de variar um pouco entre execuções.

#### Os 10 negativos que o baseline errou (leitura feita por Claude, a conferir pelo autor)

| Grupo | Itens | O que acontece |
|---|---|---|
| Nota concorda com o gabarito (1 a 2 estrelas), baseline erra | 6 | Limite do bag-of-words: ironia e gíria sem palavra de sentimento ("isso tudo isso compra um calular..."), elogio negado pelo contexto ("Não depila... modelo anterior ótimo"), texto longo e polido com queixa no meio (notebook que trava), crítica em tom brando prevista como neutra (2 itens), elogio inicial seguido de dor ("A bota é linda, mas... dói muito") |
| Nota (3 a 4 estrelas) discorda do gabarito | 4 | Textos mistos, como "produto ótimo, porém a loja deixou a desejar". O baseline foi treinado para dizer neutro/positivo nesses casos e fez isso; a divergência é de critério |

Dois pontos de cautela. Primeiro, se os 4 itens de critério fossem contados como acerto do baseline, a acurácia iria de 0,84 para 0,88:
o LLM continuaria à frente, mas por uma margem menor. É um exercício de sensibilidade, não uma correção do teste (os rótulos do teste
não foram alterados). Segundo, pelo menos um desses 4 (3 estrelas: "Gostei muito do produto, entrega rápida... o produto está sendo bom")
parece mais positivo que negativo, e o gabarito o marca como negativo: é candidato a rótulo discutível. Como o Gemini
acertou quase todos os negativos do gabarito, incluindo esses textos mistos, isso é compatível com a limitação já citada:
dois LLMs tendem a concordar entre si em casos ambíguos. Uma releitura humana desses 4 itens (sem alterar o teste) é o próximo passo barato.

## Limitações
- 200 exemplos: com 100 no teste, cada ponto percentual de acurácia é 1 item; diferenças de poucos pontos são ruído.
- Gabarito rotulado por Claude e avaliado com outro LLM (Gemini): a concordância entre dois
  modelos pode superestimar a concordância com humanos. As 3 primeiras avaliações foram decididas
  pelo autor. Ainda não há re-rotulagem humana de uma amostra.
- Classes pequenas no teste (neutro 7 itens, preco 2, atendimento 2, outro 5): métricas instáveis.
- Distribuição estratificada por estrelas, não a natural.

## Como reproduzir
```bash
pip install -r ../requirements.txt
export ANTHROPIC_API_KEY=...            # e PGHOST/PGPORT/PGUSER/PGDATABASE se não for o padrão
python prepare_sample.py                # já gerado: labeling/to_label.csv
# o gabarito já está preenchido em labeling/to_label.csv (ver "Dados" sobre quem rotulou)
python split.py
python run_eval.py --prompt v1 --split dev --runs 3
python report.py --prompt v1 --split dev
python -m pytest tests                  # testes do parsing/retry/métricas/SQL (sem API)
```
