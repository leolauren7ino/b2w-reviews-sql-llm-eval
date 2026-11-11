-- Q5. Deduplicação: quem avaliou o MESMO produto mais de uma vez com textos diferentes?
-- (as cópias idênticas já foram removidas no pandas; aqui sobram reavaliações legítimas)
WITH numeradas AS (
    SELECT reviewer_id, product_id, rating, submitted_at,
           ROW_NUMBER() OVER (PARTITION BY reviewer_id, product_id ORDER BY submitted_at) AS rn,
           count(*)     OVER (PARTITION BY reviewer_id, product_id)                       AS total
    FROM reviews
)
SELECT count(DISTINCT (reviewer_id, product_id)) AS pares_com_reavaliacao,
       count(*) FILTER (WHERE rn = 1)            AS primeiras,
       count(*) FILTER (WHERE rn > 1)            AS reavaliacoes,
       round(avg(rating) FILTER (WHERE rn = 1), 2) AS nota_primeira,
       round(avg(rating) FILTER (WHERE rn > 1), 2) AS nota_reavaliacao
FROM numeradas
WHERE total > 1;
