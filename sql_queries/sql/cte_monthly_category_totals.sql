WITH monthly_totals AS (
  SELECT
    date_trunc('month', timestamp) AS month,
    category_id,
    SUM(amount)                AS total_amount
  FROM transactions_transaction
  GROUP BY 1, 2
)
SELECT
  mt.month,
  c.name        AS category,
  mt.total_amount
FROM monthly_totals mt
JOIN transactions_category c ON c.id = mt.category_id
ORDER BY mt.month DESC, mt.total_amount DESC
LIMIT 20;
