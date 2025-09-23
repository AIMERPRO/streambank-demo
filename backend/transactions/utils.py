import logging
from typing import Any, Dict, List

from django.conf import settings
from django.db import DatabaseError, connection

logger = logging.getLogger(__name__)


def run_sql_file(filename: str) -> List[Dict[str, Any]]:
    """
    Выполняет SQL-зценарий из папки docs/sql/ и возвращает результат как список словарей.  # noqa: E501

    :param filename: имя файла внутри docs/sql/, например "get_user_stats.sql"
    :return: список строк результата, где каждая строка — dict {column_name: value}
    :raises FileNotFoundError: если файл не найден
    :raises DatabaseError: если при выполнении SQL возникает ошибка
    """
    sql_path = (settings.SQL_DIR / filename).resolve()

    if not sql_path.is_file():
        logger.error("SQL file not found: %s", sql_path)
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    try:
        raw_sql = sql_path.read_text(encoding="utf-8")
    except Exception:
        logger.exception("Failed to read SQL file %s", sql_path)
        raise

    try:
        with connection.cursor() as cursor:
            cursor.execute(raw_sql)
            columns = (
                [col[0] for col in cursor.description]
                if cursor.description
                else []
            )
            rows = cursor.fetchall()
    except DatabaseError:
        logger.exception("Error executing SQL from %s", sql_path)
        raise

    result: List[Dict[str, Any]] = [dict(zip(columns, row)) for row in rows]
    logger.debug("Executed %s: returned %d rows", filename, len(result))
    return result
