# 🛠️ Разработка

## 1. Установка зависимостей

```bash
poetry install --with dev                # линтеры, pytest, mypy
pre-commit install                       # githook'и
```

## 2. Проведение миграций
```bash
docker compose exec web python manage.py makemigrations  # создать миграции
docker compose run --rm migrate          # произвести миграции
```

## 3. Запуск тестов
```bash
pre-commit run --all-files               # запустить проверку линтеров
docker-compose up --abort-on-container-exit tests  # запустить тесты pytest
```
