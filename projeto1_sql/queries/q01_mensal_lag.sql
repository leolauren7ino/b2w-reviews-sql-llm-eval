-- Q1. Como o volume e a nota média evoluem mês a mês? (agregação por mês + LAG)
WITH mensal AS (
    SELECT date_trunc('month', submitted_at)::date AS mes,
           count(*)                                AS avaliacoes,
           round(avg(rating), 2)                   AS nota_media
    FROM reviews
    GROUP BY 1
)
SELECT mes, avaliacoes, nota_media,
       avaliacoes - LAG(avaliacoes) OVER (ORDER BY mes) AS delta_volume,
       round(100.0 * (avaliacoes - LAG(avaliacoes) OVER (ORDER BY mes))
             / LAG(avaliacoes) OVER (ORDER BY mes), 1)  AS var_pct,
       round(nota_media - LAG(nota_media) OVER (ORDER BY mes), 2) AS delta_nota
FROM mensal
ORDER BY mes;
