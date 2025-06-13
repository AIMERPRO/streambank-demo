FROM python:3.12-slim

# Установим системные зависимости для psycopg2
RUN apt-get update \
 && apt-get install -y gcc libpq-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем манифесты, чтобы кэшировать слой установки
COPY pyproject.toml poetry.lock ./

RUN pip install poetry \
 && poetry config virtualenvs.create false \
 && poetry install --without dev --no-root --no-interaction --no-ansi

# Копируем наш API-код
COPY api/ ./api

WORKDIR /app/api

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]
