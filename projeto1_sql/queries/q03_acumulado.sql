-- Q3. Soma acumulada de avaliações e % do total ao longo do tempo (SUM OVER)
WITH mensal AS (
    SELECT date_trunc('month', submitted_at)::date AS mes, count(*) AS n
    FROM reviews GROUP BY 1
)
SELECT mes, n,
       SUM(n) OVER (ORDER BY mes)                                  AS acumulado,
       round(100.0 * SUM(n) OVER (ORDER BY mes) / SUM(n) OVER (), 1) AS pct_do_total
FROM mensal
ORDER BY mes;
