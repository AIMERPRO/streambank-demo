from fastapi import FastAPI
from routers.analytics import router as analytics_router

from .core.auth import router as auth_router
from .core.exceptions import register_exception_handlers

app = FastAPI(
    title="StreamBank Analytics",
    version="1.0.0",
    description="Сервис аналитики транзакций",
)

# централизованные хэндлеры
register_exception_handlers(app)

# подключаем маршруты
app.include_router(analytics_router)
app.include_router(auth_router)
