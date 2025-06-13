# 🚀 Быстрый старт

## 1. Предварительные требования

| Инструмент  | Проверка версии      | Минимум |
|-------------|----------------------|---------|
| Docker      | `docker --version`   | 24.0+   |
| Docker Compose v2 | `docker compose version` | 2.20+ |

## 2. Клон репозитория

```bash
git clone https://github.com/<user>/streambank-demo.git
cd streambank-demo

cp .env.example .env
# при необходимости отредактируйте .env, задав пароли БД, Grafana и Flower

docker compose up --build -d

docker compose exec web python manage.py createsuperuser
# создать себе пользователя с правами Superuser
```

## 3. Какие сервисы с портами и URL будут подняты:

| Порт	 | Компонент          | 	URL                        |
|-------|--------------------|-----------------------------|
| 8000	 | Django (без Nginx) | http://localhost:8000/admin |
| 8080	 | Django (с Nginx)   | http://localhost:8080/admin |
| 8001	 | FastAPI Swagger	   | http://localhost:8001/docs  |
| 5555	 | Flower UI	         | http://localhost:5555       |
| 3000	 | Grafana	           | http://localhost:3000       |
| 9090	 | Prometheus	        | http://localhost:9090       |


## 4. Сервисы-инструменты (без Порта или URL)

| Порт	 | Компонент       | 	Команда запуска                                  |
|-------|-----------------|---------------------------------------------------|
| 8080	 | Nginx           |                                                   |
| 5432	 | PostgreSQL      |                                                   |
| 	     | Pytest          | docker-compose up --abort-on-container-exit tests |
| 	     | Worker Celery   |                                                   |
| 	     | Celery Beat     |                                                   |
| 	     | Migrate Service | docker compose run --rm migrate                   |
