# EXPLAIN antes e depois do índice

## Histórico de um cliente (filtro por reviewer_id)

```sql
SELECT review_id, product_id, rating, submitted_at FROM reviews WHERE reviewer_id = '0088df8832acccd8c266bd747c4287797235d61219ce550ddb48c006b94fa8e0' ORDER BY submitted_at
```

Índice criado: `CREATE INDEX idx_reviews_reviewer ON reviews (reviewer_id, submitted_at)`

### Antes
```
Sort  (cost=8302.93..8302.98 rows=22 width=26) (actual time=22.429..22.431 rows=29 loops=1)
  Sort Key: submitted_at
  Sort Method: quicksort  Memory: 26kB
  Buffers: shared hit=3008 read=3656
  ->  Seq Scan on reviews  (cost=0.00..8302.44 rows=22 width=26) (actual time=18.984..22.419 rows=29 loops=1)
        Filter: (reviewer_id = '0088df8832acccd8c266bd747c4287797235d61219ce550ddb48c006b94fa8e0'::text)
        Rows Removed by Filter: 131046
        Buffers: shared hit=3008 read=3656
Planning Time: 0.086 ms
Execution Time: 22.447 ms
```

### Depois
```
Sort  (cost=153.29..153.39 rows=39 width=26) (actual time=0.022..0.023 rows=29 loops=1)
  Sort Key: submitted_at
  Sort Method: quicksort  Memory: 26kB
  Buffers: shared hit=9
  ->  Bitmap Heap Scan on reviews  (cost=4.72..152.26 rows=39 width=26) (actual time=0.010..0.017 rows=29 loops=1)
        Recheck Cond: (reviewer_id = '0088df8832acccd8c266bd747c4287797235d61219ce550ddb48c006b94fa8e0'::text)
        Heap Blocks: exact=6
        Buffers: shared hit=9
        ->  Bitmap Index Scan on idx_reviews_reviewer  (cost=0.00..4.71 rows=39 width=0) (actual time=0.007..0.007 rows=29 loops=1)
              Index Cond: (reviewer_id = '0088df8832acccd8c266bd747c4287797235d61219ce550ddb48c006b94fa8e0'::text)
              Buffers: shared hit=3
Planning Time: 0.035 ms
Execution Time: 0.034 ms
```

## Avaliações recentes de um produto (product_id + ordenação por data)

```sql
SELECT review_id, rating, submitted_at FROM reviews WHERE product_id = 132532965 ORDER BY submitted_at DESC LIMIT 20
```

Índice criado: `CREATE INDEX idx_reviews_product_date ON reviews (product_id, submitted_at DESC)`

### Antes
```
Limit  (cost=8302.50..8302.51 rows=5 width=18) (actual time=19.945..19.948 rows=20 loops=1)
  Buffers: shared hit=3168 read=3496
  ->  Sort  (cost=8302.50..8302.51 rows=5 width=18) (actual time=19.944..19.946 rows=20 loops=1)
        Sort Key: submitted_at DESC
        Sort Method: top-N heapsort  Memory: 27kB
        Buffers: shared hit=3168 read=3496
        ->  Seq Scan on reviews  (cost=0.00..8302.44 rows=5 width=18) (actual time=0.024..19.930 rows=45 loops=1)
              Filter: (product_id = 132532965)
              Rows Removed by Filter: 131030
              Buffers: shared hit=3168 read=3496
Planning Time: 0.051 ms
Execution Time: 19.958 ms
```

### Depois
```
Limit  (cost=24.17..24.18 rows=5 width=18) (actual time=0.040..0.042 rows=20 loops=1)
  Buffers: shared hit=49
  ->  Sort  (cost=24.17..24.18 rows=5 width=18) (actual time=0.039..0.040 rows=20 loops=1)
        Sort Key: submitted_at DESC
        Sort Method: top-N heapsort  Memory: 27kB
        Buffers: shared hit=49
        ->  Bitmap Heap Scan on reviews  (cost=4.46..24.11 rows=5 width=18) (actual time=0.011..0.031 rows=45 loops=1)
              Recheck Cond: (product_id = 132532965)
              Heap Blocks: exact=45
              Buffers: shared hit=49
              ->  Bitmap Index Scan on idx_reviews_product_date  (cost=0.00..4.46 rows=5 width=0) (actual time=0.006..0.006 rows=45 loops=1)
                    Index Cond: (product_id = 132532965)
                    Buffers: shared hit=4
Planning Time: 0.038 ms
Execution Time: 0.053 ms
```
