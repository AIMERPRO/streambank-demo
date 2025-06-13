from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # каждую ночь в 2:00 запускаем импорт
    "import-nightly": {
        "task": "transactions.tasks.import_csv",
        "schedule": crontab(hour=2, minute=0),
        "args": ["/app/data/sample_transactions.csv"],
    },
    # в 3:00 — детекция аномалий
    "detect-nightly": {
        "task": "transactions.tasks.detect_anomalies",
        "schedule": crontab(hour=3, minute=0),
        "args": [3],
    },
}
