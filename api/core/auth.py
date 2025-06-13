from datetime import datetime, timedelta
from typing import Any, Dict, cast

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from passlib.hash import django_pbkdf2_sha256
from psycopg2.extensions import connection as Connection

from api.core.config import settings
from api.core.database import get_db

router = APIRouter(tags=["auth"])


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    conn: Connection = Depends(get_db),
):
    """
    1) Ищем пользователя в auth_user по username
    2) Берём его password (хеш) и проверяем через passlib
    3) Если всё ок — возвращаем JWT (access + тип)
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, password FROM auth_user WHERE username = %s;",
            (form_data.username,),
        )
        row = cast(Dict[str, Any], cur.fetchone())

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id, hashed_password = row["id"], row["password"]
    # Проверяем plain→hash
    if not django_pbkdf2_sha256.verify(form_data.password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Генерируем JWT
    access_expires = timedelta(minutes=30)
    expire = datetime.utcnow() + access_expires
    to_encode = {"sub": form_data.username, "exp": expire, "user_id": user_id}
    token = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return {"access_token": token, "token_type": "bearer"}
