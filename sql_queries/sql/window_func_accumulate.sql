SELECT
  id,
  timestamp::date AS date,
  amount,
  SUM(amount) OVER (
    PARTITION BY date_trunc('month', timestamp)
    ORDER BY timestamp
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS running_monthly_total,
  RANK() OVER (
    PARTITION BY date_trunc('month', timestamp)
    ORDER BY amount DESC
  ) AS rank_in_month
FROM transactions_transaction
WHERE timestamp >= now() - INTERVAL '90 days'
ORDER BY timestamp DESC
LIMIT 50;
