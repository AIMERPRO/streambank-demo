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
    # 1. Собираем путь к файлу через pathlib для читаемости
    sql_path = (settings.SQL_DIR / filename).resolve()

    # 2. Проверяем, что файл существует
    if not sql_path.is_file():
        logger.error("SQL file not found: %s", sql_path)
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    # 3. Считываем весь SQL из файла
    try:
        raw_sql = sql_path.read_text(encoding="utf-8")
    except Exception:
        logger.exception("Failed to read SQL file %s", sql_path)
        raise

    # 4. Выполняем SQL и собираем результаты
    try:
        with connection.cursor() as cursor:
            cursor.execute(raw_sql)
            # Описание колонок: cursor.description может быть None, если нет результата # noqa: E501
            columns = (
                [col[0] for col in cursor.description]
                if cursor.description
                else []
            )
            rows = cursor.fetchall()
    except DatabaseError:
        logger.exception("Error executing SQL from %s", sql_path)
        # Пробрасываем дальше, чтобы вызывающая сторона могла обработать или залогировать # noqa: E501
        raise

    # 5. Конвертируем результат в список словарей
    result: List[Dict[str, Any]] = [dict(zip(columns, row)) for row in rows]
    logger.debug("Executed %s: returned %d rows", filename, len(result))
    return result
