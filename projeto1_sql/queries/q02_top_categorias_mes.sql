-- Q2. Quais as 3 categorias mais avaliadas em cada mês? (CTE + RANK particionado)
WITH por_cat AS (
    SELECT date_trunc('month', submitted_at)::date AS mes,
           category_lv1, count(*) AS n
    FROM reviews
    GROUP BY 1, 2
), ranqueado AS (
    SELECT *, RANK() OVER (PARTITION BY mes ORDER BY n DESC) AS posicao
    FROM por_cat
)
SELECT mes, posicao, category_lv1, n
FROM ranqueado
WHERE posicao <= 3
ORDER BY mes, posicao;
