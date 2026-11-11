-- Q7. Quais marcas estão acima da média da própria categoria? (AVG OVER PARTITION)
WITH marca AS (
    SELECT category_lv1, brand, count(*) AS n, avg(rating) AS nota
    FROM reviews
    WHERE brand IS NOT NULL
    GROUP BY 1, 2
    HAVING count(*) >= 100
), comp AS (
    SELECT *, AVG(nota) OVER (PARTITION BY category_lv1) AS media_categoria
    FROM marca
)
SELECT category_lv1, brand, n, round(nota, 2) AS nota,
       round(media_categoria, 2) AS media_categoria,
       round(nota - media_categoria, 2) AS diferenca
FROM comp
ORDER BY diferenca DESC
LIMIT 10;
