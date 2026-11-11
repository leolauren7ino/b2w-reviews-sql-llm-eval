-- Q10. Clientes recorrentes: quanto tempo entre duas avaliações consecutivas? (LAG em timestamp)
WITH seq AS (
    SELECT reviewer_id, submitted_at,
           LAG(submitted_at) OVER (PARTITION BY reviewer_id ORDER BY submitted_at) AS anterior
    FROM reviews
), intervalos AS (
    SELECT extract(epoch FROM (submitted_at - anterior)) / 86400.0 AS dias
    FROM seq
    WHERE anterior IS NOT NULL
)
SELECT count(*)                                            AS pares_consecutivos,
       round(percentile_cont(0.5) WITHIN GROUP (ORDER BY dias)::numeric, 1) AS mediana_dias,
       round(percentile_cont(0.9) WITHIN GROUP (ORDER BY dias)::numeric, 1) AS p90_dias,
       round(100.0 * avg((dias < 1)::int), 1)             AS pct_no_mesmo_dia
FROM intervalos;
