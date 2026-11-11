# Resultados das 10 perguntas

## Q1. Como o volume e a nota média evoluem mês a mês? (agregação por mês + LAG)

```sql
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
```

| mes | avaliacoes | nota_media | delta_volume | var_pct | delta_nota |
|---|---|---|---|---|---|
| 2018-01-01 | 34570 | 3.60 | None | None | None |
| 2018-02-01 | 11616 | 3.42 | -22954 | -66.4 | -0.18 |
| 2018-03-01 | 29765 | 3.50 | 18149 | 156.2 | 0.08 |
| 2018-04-01 | 29736 | 3.50 | -29 | -0.1 | 0.00 |
| 2018-05-01 | 25388 | 3.43 | -4348 | -14.6 | -0.07 |

## Q2. Quais as 3 categorias mais avaliadas em cada mês? (CTE + RANK particionado)

```sql
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
```

| mes | posicao | category_lv1 | n |
|---|---|---|---|
| 2018-01-01 | 1 | Celulares e Smartphones | 5715 |
| 2018-01-01 | 2 | Eletroportáteis | 3365 |
| 2018-01-01 | 3 | Beleza e Perfumaria | 2421 |
| 2018-02-01 | 1 | Celulares e Smartphones | 1928 |
| 2018-02-01 | 2 | Eletroportáteis | 1026 |
| 2018-02-01 | 3 | Beleza e Perfumaria | 858 |
| 2018-03-01 | 1 | Celulares e Smartphones | 4506 |
| 2018-03-01 | 2 | Eletroportáteis | 2906 |
| 2018-03-01 | 3 | Utilidades Domésticas | 2019 |
| 2018-04-01 | 1 | Celulares e Smartphones | 4582 |
| 2018-04-01 | 2 | Eletroportáteis | 2589 |
| 2018-04-01 | 3 | Beleza e Perfumaria | 1944 |
| 2018-05-01 | 1 | Celulares e Smartphones | 3871 |
| 2018-05-01 | 2 | Eletroportáteis | 1809 |
| 2018-05-01 | 3 | Beleza e Perfumaria | 1734 |

## Q3. Soma acumulada de avaliações e % do total ao longo do tempo (SUM OVER)

```sql
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
```

| mes | n | acumulado | pct_do_total |
|---|---|---|---|
| 2018-01-01 | 34570 | 34570 | 26.4 |
| 2018-02-01 | 11616 | 46186 | 35.2 |
| 2018-03-01 | 29765 | 75951 | 57.9 |
| 2018-04-01 | 29736 | 105687 | 80.6 |
| 2018-05-01 | 25388 | 131075 | 100.0 |

## Q4. Melhores e piores produtos por nota, só com amostra mínima (>= 40 avaliações).

```sql
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
```

| rank_melhor | dense_melhor | rank_pior | produto | categoria | n | nota_media |
|---|---|---|---|---|---|---|
| 1 | 1 | 327 | Fraldas Descartáveis Huggies Primeiros 100 dias P  | Bebês | 64 | 4.95 |
| 2 | 2 | 326 | Fraldas Huggies Turma Da Mônica Soft Touch M 46un. | Bebês | 119 | 4.86 |
| 3 | 3 | 323 | Bandeja De Isopor Branca Hf-0 Hamburgueira Com 400 | Papelaria | 45 | 4.73 |
| 3 | 3 | 323 | iPhone 8 Cinza Espacial 64GB Tela 4.7" IOS 11 4G W | Celulares e Smartphones | 45 | 4.73 |
| 3 | 3 | 323 | Mochila Para Notebook Dell Professional 15,6" Pret | Malas e Acessórios | 66 | 4.73 |
| 322 | 151 | 5 | Game God Of War - PS4 | Games | 255 | 2.38 |
| 322 | 151 | 5 | Notebook Positivo Motion Q232A Intel Atom Quad Cor | Informática | 55 | 2.38 |
| 324 | 152 | 4 | Mini Boneca Supresa - LOL - Lil Outrageous Littles | Brinquedos | 45 | 2.27 |
| 325 | 153 | 3 | Purificador de Água Polar WP1000A WP2000A Eletrôni | Eletroportáteis | 90 | 2.23 |
| 326 | 154 | 2 | Celular Dual Chip LG B220 Desbloqueado 32MB 2G Rád | Celulares e Smartphones | 43 | 2.21 |
| 327 | 155 | 1 | Purificador de Água Polar WP1000B/WP2000B Eletrôni | Eletroportáteis | 47 | 2.04 |

## Q5. Deduplicação: quem avaliou o MESMO produto mais de uma vez com textos diferentes?

```sql
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
```

| pares_com_reavaliacao | primeiras | reavaliacoes | nota_primeira | nota_reavaliacao |
|---|---|---|---|---|
| 800 | 800 | 858 | 1.76 | 1.86 |

## Q6. A "recomenda a um amigo" é coerente com a nota? Onde estão as contradições?

```sql
-- Q6. A "recomenda a um amigo" é coerente com a nota? Onde estão as contradições?
SELECT rating,
       count(*)                                                      AS n,
       round(100.0 * avg((recommends)::int), 1)                      AS pct_recomenda,
       round(100.0 * count(*) / SUM(count(*)) OVER (), 1)            AS pct_do_total
FROM reviews
WHERE recommends IS NOT NULL
GROUP BY rating
ORDER BY rating;
```

| rating | n | pct_recomenda | pct_do_total |
|---|---|---|---|
| 1 | 26531 | 2.9 | 20.2 |
| 2 | 8272 | 24.6 | 6.3 |
| 3 | 16192 | 88.6 | 12.4 |
| 4 | 32260 | 98.4 | 24.6 |
| 5 | 47802 | 98.5 | 36.5 |

## Q7. Quais marcas estão acima da média da própria categoria? (AVG OVER PARTITION)

```sql
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
```

| category_lv1 | brand | n | nota | media_categoria | diferenca |
|---|---|---|---|---|---|
| Informática e Acessórios | microsoft | 104 | 4.34 | 3.77 | 0.56 |
| Informática e Acessórios | logitech | 139 | 4.32 | 3.77 | 0.54 |
| Informática | samsung | 394 | 3.88 | 3.34 | 0.53 |
| Beleza e Perfumaria | taiff | 304 | 4.17 | 3.67 | 0.50 |
| Eletroportáteis | philips walita | 546 | 4.26 | 3.81 | 0.45 |
| Celulares e Smartphones | apple | 231 | 4.35 | 3.90 | 0.44 |
| Eletrodomésticos | consul | 603 | 3.98 | 3.57 | 0.41 |
| Bebês | fisher price | 123 | 4.12 | 3.73 | 0.39 |
| Beleza e Perfumaria | philips | 718 | 4.03 | 3.67 | 0.36 |
| Informática e Acessórios | dell | 144 | 4.13 | 3.77 | 0.35 |

## Q8. Estados com maior % de nota 1 (insatisfação), com volume mínimo.

```sql
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
```

| posicao | state | n | nota_media | pct_nota_1 |
|---|---|---|---|---|
| 1 | PI | 686 | 3.40 | 23.3 |
| 1 | RJ | 17397 | 3.41 | 23.3 |
| 3 | CE | 2138 | 3.48 | 22.8 |
| 4 | MS | 823 | 3.43 | 22.6 |
| 5 | BA | 4749 | 3.38 | 22.1 |
| 6 | PA | 1477 | 3.49 | 21.6 |
| 6 | MT | 979 | 3.41 | 21.6 |
| 8 | GO | 2506 | 3.52 | 21.1 |
| 8 | MA | 1197 | 3.44 | 21.1 |
| 10 | SC | 4436 | 3.49 | 21.0 |
| 11 | AL | 722 | 3.55 | 20.9 |
| 12 | ES | 3009 | 3.47 | 20.4 |
| 13 | RN | 904 | 3.54 | 20.0 |
| 13 | SE | 529 | 3.51 | 20.0 |
| 13 | RS | 6573 | 3.53 | 20.0 |
| 16 | PB | 871 | 3.53 | 19.7 |
| 16 | MG | 16155 | 3.51 | 19.7 |
| 18 | SP | 48819 | 3.52 | 19.3 |
| 19 | DF | 2372 | 3.52 | 19.2 |
| 20 | PE | 2908 | 3.57 | 18.7 |
| 21 | PR | 6684 | 3.63 | 17.9 |

## Q9. Texto longo = reclamação? Nota média e % de nota 1 por faixa de tamanho do texto.

```sql
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
```

| tamanho | n | nota_media | pct_nota_1 | pct_nota_5 |
|---|---|---|---|---|
| 1) < 40 chars | 54 | 4.00 | 5.6 | 46.3 |
| 2) 40-99 | 67981 | 3.88 | 11.5 | 42.9 |
| 3) 100-199 | 39127 | 3.36 | 23.4 | 34.1 |
| 4) 200+ | 20758 | 2.74 | 38.1 | 22.6 |

## Q10. Clientes recorrentes: quanto tempo entre duas avaliações consecutivas? (LAG em timestamp)

```sql
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
```

| pares_consecutivos | mediana_dias | p90_dias | pct_no_mesmo_dia |
|---|---|---|---|
| 18082 | 2.1 | 54.7 | 46.4 |
