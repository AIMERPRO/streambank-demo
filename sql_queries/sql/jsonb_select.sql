
ALTER TABLE transactions_transaction
    ADD COLUMN IF NOT EXISTS data JSONB;

UPDATE transactions_transaction
SET data =
  '{"merchant":"Store A","tags":["groceries","food"],"location":{"city":"Paris","lat":48.8566}}'
WHERE id = 1;
SELECT
  id,
  data ->> 'merchant'            AS merchant,
  data -> 'location' ->> 'city'  AS city,
  data -> 'tags'                 AS tags
FROM transactions_transaction
WHERE data -> 'location' ->> 'city' = 'Paris';
