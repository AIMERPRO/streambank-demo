FROM python:3.12-slim

# Установка зависимостей системы
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем только манифесты и README, чтобы кэшировать слой poetry-install
COPY pyproject.toml poetry.lock README.md ./

# Устанавливаем Poetry и зависимости без создания venv
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --without dev --no-root --no-interaction --no-ansi
# Копируем остальной код
COPY backend/ ./backend/

WORKDIR /app/backend

# Собираем статические (если нужно)
# RUN python manage.py collectstatic --no-input

# Запускаем приложение
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
