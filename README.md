# StreamBank Demo

[![CI](https://github.com/AIMERPRO/streambank-demo/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/AIMERPRO/streambank-demo/actions/workflows/ci-cd.yml)
[![Docker Ready](https://img.shields.io/badge/docker-ready-blue)](#quick-start)
Документация 👉 **[StreamBank Docs](https://aimerpro.github.io/streambank-demo/)**
[![Docs](https://img.shields.io/badge/docs-site-green)](https://aimerpro.github.io/streambank-demo/)

> StreamBank — PET финтех проект: Django + FastAPI + Celery, покрытый CI, мониторингом и документацией.

## Quick Start

```bash
git clone https://github.com/<user>/streambank-demo.git
cd streambank-demo
cp .env.example .env          # задайте пароли
docker-compose up --build -d  # поднимет БД, сервисы, Flower, Grafana, автоматически промигрирует через сервис Migrate
docker-compose exec web python manage.py createsuperuser  # создаст пользователя с правами Superuser
open http://localhost:8000/admin    # Django приложения (сайт администратора)
open http://localhost:8001/docs  # FastAPI Swagger
```
