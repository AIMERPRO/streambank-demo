from typing import Any, Dict, List, cast

from psycopg2.extensions import connection as Connection

from api.schemas.analytics import CategoryStats


class AnalyticsRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    def get_average_amount(self) -> float:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT AVG(amount) AS average_amount"
                " FROM transactions_transaction;"
            )
            row = cast(Dict[str, Any], cur.fetchone())
        return float(row["average_amount"] or 0)

    def get_top_categories(self, limit: int) -> List[CategoryStats]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.name,
                       SUM(t.amount)      AS total_amount,
                       COUNT(*)           AS transaction_count
                FROM transactions_category c
                JOIN transactions_transaction t
                  ON t.category_id = c.id
                GROUP BY c.name
                ORDER BY total_amount DESC
                LIMIT %s;
            """,
                (limit,),
            )
            rows = cast(Dict[dict, Any], cur.fetchall())
        return [CategoryStats(**r) for r in rows]

    def get_p95_amount(self) -> float:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT percentile_cont(0.95)
                       WITHIN GROUP (ORDER BY amount) AS p95_amount
                FROM transactions_transaction;
            """
            )
            row = cast(Dict[str, Any], cur.fetchone())
        return float(row["p95_amount"] or 0)
