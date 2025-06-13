from typing import Generator

import psycopg2
import psycopg2.extras

from .config import settings


def get_db() -> Generator[psycopg2.extensions.connection, None, None]:
    """
    FastAPI dependency: открывает и закрывает соединение к Postgres.
    """
    conn = psycopg2.connect(
        settings.database_url, cursor_factory=psycopg2.extras.RealDictCursor
    )
    try:
        yield conn
    finally:
        conn.close()
