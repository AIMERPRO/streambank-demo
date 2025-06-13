from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from psycopg2 import Error as Psycopg2Error
from pydantic import ValidationError


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(Psycopg2Error)
    async def db_error_handler(request: Request, exc: Psycopg2Error):
        return JSONResponse(
            status_code=500, content={"detail": "Ошибка работы с базой данных"}
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # пропускаем свои HTTPException
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.detail}
        )
