# 🏦 StreamBank Demo

> **StreamBank** — учебный финтех-бэкенд с примерами «полного цикла»:
> Django + FastAPI + Celery, покрытые CI, метриками и документацией.

[![CI](https://github.com/AIMERPRO/streambank-demo/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/AIMERPRO/streambank-demo/actions/workflows/ci-cd.yml)
[![Docker ready](https://img.shields.io/badge/docker-ready-blue)](getting-started.md)

---

## ✨ Что внутри

| Слой | Технология         | Ключевые возможности                       |
|------|--------------------|--------------------------------------------|
| **Web / Admin** | Django 5.2.3       | Админ-панель, ORM, миграции                |
| **Public API**  | FastAPI 0.115.12   | Получение информации для аналитиков по API |
| **Tasks**       | Celery 5 + Redis 6 | Детект аномалий в фоне                     |
| **Observability** | Prometheus + Grafana | Отслеживание метрик                        |
| **CI** | GitHub Actions     | linters • mypy • pytest                    |


## 🚀 [Быстрый старт](getting-started.md)
