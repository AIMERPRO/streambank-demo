# 🤝 Contributing to StreamBank Demo

## 1. Quick Checklist

1. Сделайте форк → новую ветку из `master`.
2. `poetry install --with dev && pre-commit install`.
3. Пишите код; убедитесь, что `pre-commit run --all-files && docker compose up --abort-on-container-exit tests` пройдены.
4. Откройте Pull Request; CI должен пройти без ошибок.

## 2. Style & Tooling

| Что               | Правило                                          |
|-------------------|--------------------------------------------------|
| **Commits**       | Conventional Commits (`feat:`, `fix:`, `docs:`…) |
| **Black + Isort** | запускаются авторматтером pre-commit             |
| **Mypy**          | код 100 % типизирован                            |
| **Tests**         | Pytest + Coverage ≥ 90 %                         |
