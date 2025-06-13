import csv
import logging
import os
import sys
from multiprocessing import Pool, cpu_count

from django.utils import timezone

# -------------------------------------------------------------------
# Настройка Django:
# 1. Добавляем корень проекта (где находится manage.py) в sys.path,
#    чтобы правильно решать импорты Django-приложения.
# 2. Устанавливаем переменную окружения для настроек Django.
# 3. Вызываем django.setup() для инициализации ORM.
# -------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)  # /app/backend
sys.path.insert(0, PROJECT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from transactions.models import Category, Transaction  # noqa: E402

# -------------------------------------------------------------------
# Настройка логирования для удобства отладки и мониторинга процесса
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def _process_row(row):
    """
    Преобразует одну строку CSV в объект Transaction (но не сохраняет его).
    - Парсит timestamp в timezone-aware datetime.
    - Ищет или создаёт категорию.
    - Создаёт экземпляр модели, не вызывая .save().
    """
    ts = timezone.datetime.fromisoformat(row["timestamp"])
    cat, _ = Category.objects.get_or_create(name=row["category_name"])
    return Transaction(
        timestamp=ts,
        amount=row["amount"],
        currency=row.get("currency", "USD"),
        description=row.get("description", ""),
        category=cat,
    )


def _import_batch(rows):
    """
    Обрабатывает пакет строк CSV:
    - Преобразует каждую строку в Transaction.
    - Сохраняет их в БД одним запросом bulk_create.
    Возвращает число созданных записей.
    """
    objs = [_process_row(r) for r in rows]
    Transaction.objects.bulk_create(
        objs
    )  # Сохраняем пачкой — быстрее, чем save() в цикле
    return len(objs)


def _chunked_reader(path, chunk_size):
    """
    Читает CSV-файл порциями (batch) по chunk_size строк
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        batch = []
        for row in reader:
            batch.append(row)
            if len(batch) >= chunk_size:
                yield batch
                batch = []
        if batch:
            yield batch


def import_transactions_multiprocess(path: str, chunk_size: int = 500) -> int:
    """
    Импорт транзакций в нескольких процессах:
    - Разбиваем CSV на чанки.
    - Параллельно обрабатываем каждый чанк в Pool.
    - Возвращаем общее количество импортированных записей.

    ВАЖНО: Django ORM не полностью безопасен при форке,
    поэтому можно после pool.map вызывать django.db.close_old_connections()
    """
    total = 0
    pool_size = min(cpu_count(), 4)

    logger.info(
        f"Запуск импорта: файл={path}, "
        f" chunk_size={chunk_size}, "
        f" processes={pool_size}"
    )

    # Закрываем старые соединения перед форком
    from django.db import connections

    for conn in connections.all():
        conn.close_if_unusable_or_obsolete()

    with Pool(pool_size) as pool:
        for count in pool.map(
            _import_batch, _chunked_reader(path, chunk_size)
        ):
            total += count
            logger.info(f"Обработан пакет: {count} записей (итого {total})")

    logger.info(f"Импорт завершён: всего {total} транзакций")
    return total


def main():
    if len(sys.argv) != 2:
        logger.error("Неправильное количество аргументов.")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.isfile(path):
        logger.error(f"Файл не найден: {path}")
        print(f"Error: file not found: {path}")
        sys.exit(1)

    try:
        import_transactions_multiprocess(path)

    except Exception as exc:
        logger.exception(f"Ошибка при импорте транзакций: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
