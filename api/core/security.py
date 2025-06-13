from typing import Any, Dict, cast

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from psycopg2.extensions import connection as Connection

from .config import settings
from .database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    1. Декодируем токен и получаем payload
    2. Извлекаем user_id
    3. Из БД достаём запись из auth_user
    4. Возвращаем словарь с полями пользователя
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: Any = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Забираем пользователя из Django-таблицы auth_user
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, username, email, is_active"
            " FROM auth_user WHERE id = %s;",
            (user_id,),
        )
        row = cast(Dict[str, Any], cur.fetchone())

    if not row or not row.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive or non-existent user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "id": row["id"],
        "username": row["username"],
        "email": row["email"],
    }
