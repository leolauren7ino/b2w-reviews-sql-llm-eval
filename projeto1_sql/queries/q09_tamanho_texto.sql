-- Q9. Texto longo = reclamação? Nota média e % de nota 1 por faixa de tamanho do texto.
WITH faixa AS (
    SELECT rating,
           CASE WHEN length(review_text) < 40  THEN '1) < 40 chars'
                WHEN length(review_text) < 100 THEN '2) 40-99'
                WHEN length(review_text) < 200 THEN '3) 100-199'
                ELSE                                '4) 200+' END AS tamanho
    FROM reviews
    WHERE review_text IS NOT NULL
)
SELECT tamanho, count(*) AS n,
       round(avg(rating), 2) AS nota_media,
       round(100.0 * avg((rating = 1)::int), 1) AS pct_nota_1,
       round(100.0 * avg((rating = 5)::int), 1) AS pct_nota_5
FROM faixa
GROUP BY tamanho
ORDER BY tamanho;
