-- Q8. Estados com maior % de nota 1 (insatisfação), com volume mínimo.
WITH uf AS (
    SELECT state, count(*) AS n,
           round(avg(rating), 2) AS nota_media,
           round(100.0 * avg((rating = 1)::int), 1) AS pct_nota_1
    FROM reviews
    WHERE state IS NOT NULL
    GROUP BY state
    HAVING count(*) >= 500
)
SELECT RANK() OVER (ORDER BY pct_nota_1 DESC) AS posicao, *
FROM uf
ORDER BY posicao;
