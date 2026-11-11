# Projeto 2 — Classificador de avaliações com LLM e avaliação honesta

> **Estado deste README: esqueleto.** O pipeline está construído e testado, mas **nenhum número
> abaixo existe ainda**: faltam o gabarito rotulado por você e uma chave de API. Os trechos
> marcados com `⟦…⟧` devem ser preenchidos com a saída de `report.py`, não com estimativas.
> Um README com números inventados é o oposto do que este projeto quer provar.

## A pergunta
Dá para confiar num LLM para classificar avaliações em português por **sentimento** e **tema**?
Quanto, onde ele erra, e o quanto o resultado muda de uma execução para outra?

## Dados
B2W-Reviews01 (avaliações reais do e-commerce brasileiro, ~132 mil linhas), já limpo no Projeto 1.
Gabarito: **200 avaliações rotuladas por mim, às cegas quanto à nota em estrelas** (40 por estrela,
então a distribuição *não* é a natural — as métricas valem para este conjunto).
Divisão fixa (seed 42), estratificada por sentimento: **100 dev** (para ajustar o prompt) e
**100 test** (usado uma única vez por versão final de prompt; o código recusa uma segunda).

## Pipeline
`prepare_sample.py` → *(rotulagem manual)* → `split.py` → `run_eval.py` → `report.py`

- Saída do modelo em JSON, validada com pydantic (`schema.py`, sem campos extras, valores só da taxonomia).
- `llm.py` trata JSON quebrado/envolto em prosa, valores fora da taxonomia, `refusal`/`max_tokens` e erros
  de API: retry de até 3 tentativas devolvendo o erro ao modelo; tudo logado. Resposta que nunca fica
  válida **conta como erro** (não é descartada, senão a acurácia infla).
- Tudo vai para o Postgres (`gold`, `runs`, `predictions`, com a resposta bruta) e as fatias de erro
  são SQL (`sql/slices.sql`).
- Observação técnica: os modelos atuais da API não aceitam `temperature`; a variação entre execuções
  é a do amostrador padrão. Usei `effort: low`, adequado a classificação.

## Resultados
⟦Tabela: acurácia, precisão, recall e F1 por classe — v1 no dev — colar de `reports/v1_dev.md`⟧

**Consistência entre execuções** (mesmo prompt, 3 execuções): ⟦X de 100 itens mudaram de rótulo⟧.
⟦Mostrar 2–3 exemplos reais de item instável com os textos.⟧

## Análise de erros
Li os ⟦N⟧ erros um a um (`reports/v1_dev_erros.csv`, coluna `causa`):

| Causa | Itens | Exemplo real |
|---|---|---|
| Ambiguidade genuína | ⟦⟧ | ⟦texto⟧ |
| Viés/limitação do modelo | ⟦⟧ | ⟦texto⟧ |
| **Meu rótulo estava errado** | ⟦⟧ | ⟦texto⟧ |
| Instrução ruim no prompt | ⟦⟧ | ⟦texto⟧ |

## O que mudei no prompt e o efeito
Ver `prompts/CHANGELOG.md`. ⟦v1 → v2: o que mudou, por quê (qual erro), efeito no **dev**.⟧
Teste final (uma vez): ⟦números do test⟧. Diferença dev vs test: ⟦⟧ — ⟦se o dev subiu e o test não, o prompt foi ajustado ao dev.⟧

## Limitações
- 200 exemplos: com 100 no teste, cada ponto percentual de acurácia é 1 item; diferenças de poucos pontos são ruído.
- Um único rotulador (eu): o teto de acurácia é a minha própria consistência (⟦re-rotulagem de 30 itens: X% de concordância comigo mesmo⟧).
- Distribuição estratificada por estrelas, não a natural.

## Como reproduzir
```bash
pip install -r ../requirements.txt
export ANTHROPIC_API_KEY=...            # e PGHOST/PGPORT/PGUSER/PGDATABASE se não for o padrão
python prepare_sample.py                # já gerado: labeling/to_label.csv
# rotule labeling/to_label.csv seguindo labeling/GUIA_DE_ROTULAGEM.md
python split.py
python run_eval.py --prompt v1 --split dev --runs 3
python report.py --prompt v1 --split dev
python -m pytest tests                  # testes do parsing/retry/métricas/SQL (sem API)
```
