-- Fatias de erro. Parâmetros: %(prompt)s, %(split)s. Cada bloco "-- name:" vira uma seção do relatório.
-- Erro = previsão diferente do gabarito OU resposta inválida (conta como erro).

-- name: erro_por_classe_sentimento
SELECT g.sentimento AS classe_real, count(*) AS n,
       round(100.0 * avg((p.sentimento IS DISTINCT FROM g.sentimento)::int), 1) AS pct_erro
FROM predictions p JOIN runs r USING (run_id) JOIN gold g USING (review_id)
WHERE r.prompt_version = %(prompt)s AND r.split = %(split)s
GROUP BY 1 ORDER BY pct_erro DESC;

-- name: erro_por_classe_tema
SELECT g.tema AS classe_real, count(*) AS n,
       round(100.0 * avg((p.tema IS DISTINCT FROM g.tema)::int), 1) AS pct_erro
FROM predictions p JOIN runs r USING (run_id) JOIN gold g USING (review_id)
WHERE r.prompt_version = %(prompt)s AND r.split = %(split)s
GROUP BY 1 ORDER BY pct_erro DESC;

-- name: erro_por_tamanho_texto
SELECT CASE WHEN g.text_len < 80 THEN '1) <80' WHEN g.text_len < 160 THEN '2) 80-159'
            WHEN g.text_len < 300 THEN '3) 160-299' ELSE '4) 300+' END AS faixa,
       count(*) AS n,
       round(100.0 * avg((p.sentimento IS DISTINCT FROM g.sentimento)::int), 1) AS pct_erro_sentimento,
       round(100.0 * avg((p.tema IS DISTINCT FROM g.tema)::int), 1) AS pct_erro_tema
FROM predictions p JOIN runs r USING (run_id) JOIN gold g USING (review_id)
WHERE r.prompt_version = %(prompt)s AND r.split = %(split)s
GROUP BY 1 ORDER BY 1;

-- name: erro_por_estrelas_originais
-- Estrelas não entram no rótulo; aqui servem para ver onde nota e texto discordam.
SELECT g.stars, count(*) AS n,
       round(100.0 * avg((p.sentimento IS DISTINCT FROM g.sentimento)::int), 1) AS pct_erro_sentimento
FROM predictions p JOIN runs r USING (run_id) JOIN gold g USING (review_id)
WHERE r.prompt_version = %(prompt)s AND r.split = %(split)s
GROUP BY 1 ORDER BY 1;

-- name: instabilidade_entre_execucoes
-- Itens cuja previsão de sentimento mudou entre execuções do MESMO prompt.
WITH por_item AS (
    SELECT p.review_id, count(DISTINCT p.sentimento) AS rotulos_distintos,
           count(*) AS execucoes
    FROM predictions p JOIN runs r USING (run_id)
    WHERE r.prompt_version = %(prompt)s AND r.split = %(split)s
    GROUP BY 1)
SELECT rotulos_distintos, count(*) AS itens FROM por_item GROUP BY 1 ORDER BY 1;

-- name: respostas_quebradas
SELECT count(*) AS total, count(*) FILTER (WHERE NOT valid) AS invalidas,
       count(*) FILTER (WHERE valid AND attempts > 1) AS validas_apos_retry,
       round(avg(latency_ms)) AS latencia_media_ms
FROM predictions p JOIN runs r USING (run_id)
WHERE r.prompt_version = %(prompt)s AND r.split = %(split)s;
