from decimal import Decimal

from celery import shared_task
from django.db.models import Avg, Q, StdDev
from scripts.import_csv import import_transactions_multiprocess

from .models import Transaction


@shared_task
def detect_anomalies(threshold_std=3):
    """
    Помечает транзакции аномалиями, если amount выходит
    за пределы [mean - threshold_std*std, mean + threshold_std*std].

    :param threshold_std: Порог в сигмах (σ), по умолчанию 3.
    :return: Словарь с ключами:
             - mean: среднее значение (Decimal)
             - std: стандартное отклонение (Decimal)
             - threshold: использованный порог (int|float)
             - marked: число помеченных записей (int)
    """

    # Получаем статистику по полю amount
    stats = Transaction.objects.aggregate(
        mean=Avg("amount"), std=StdDev("amount")
    )
    mean, std = stats["mean"] or 0, stats["std"] or 0

    # Вычисляем границы аномальности
    threshold = Decimal(str(threshold_std))
    lower, upper = mean - threshold * std, mean + threshold * std

    # Выбираем транзакции, не помеченные ранее, которые выходят за границы
    qs = Transaction.objects.filter(
        Q(amount__lt=lower) | Q(amount__gt=upper), is_anomaly=False
    )
    updated = qs.update(is_anomaly=True)

    return {
        "mean": mean,
        "std": std,
        "threshold": threshold_std,
        "marked": updated,
    }


@shared_task
def import_csv(path, chunk_size=500):
    """
    Запускает мультипроцессный импорт транзакций из CSV-файла.

    :param path: Путь к CSV-файлу.
    :param chunk_size: Размер одной пачки строк для обработки.
    :return: {'imported': общее число импортированных записей}
    """

    imported = import_transactions_multiprocess(path, chunk_size)
    return {"imported": imported}
