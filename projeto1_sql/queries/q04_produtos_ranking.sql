-- Q4. Melhores e piores produtos por nota, só com amostra mínima (>= 40 avaliações).
-- Empates tratados: RANK (pula posições) vs DENSE_RANK (não pula).
WITH prod AS (
    SELECT product_id, max(product_name) AS produto, max(category_lv1) AS categoria,
           count(*) AS n, round(avg(rating), 2) AS nota_media
    FROM reviews
    GROUP BY product_id
    HAVING count(*) >= 40
), rk AS (
    SELECT *, RANK()       OVER (ORDER BY nota_media DESC) AS rank_melhor,
              DENSE_RANK() OVER (ORDER BY nota_media DESC) AS dense_melhor,
              RANK()       OVER (ORDER BY nota_media ASC)  AS rank_pior
    FROM prod
)
SELECT rank_melhor, dense_melhor, rank_pior, left(produto, 50) AS produto, categoria, n, nota_media
FROM rk
WHERE rank_melhor <= 5 OR rank_pior <= 5
ORDER BY rank_melhor;
