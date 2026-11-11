-- Q6. A "recomenda a um amigo" é coerente com a nota? Onde estão as contradições?
SELECT rating,
       count(*)                                                      AS n,
       round(100.0 * avg((recommends)::int), 1)                      AS pct_recomenda,
       round(100.0 * count(*) / SUM(count(*)) OVER (), 1)            AS pct_do_total
FROM reviews
WHERE recommends IS NOT NULL
GROUP BY rating
ORDER BY rating;
