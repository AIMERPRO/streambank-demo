FROM python:3.12-slim

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ../pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root --no-ansi

COPY . .

CMD ["pytest", "--maxfail=1", "--disable-warnings", "-vv", \
     "--cov=transactions", "--cov=api", "--cov-report=term-missing", "--cov-report=html"]
