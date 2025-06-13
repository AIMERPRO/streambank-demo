from typing import TYPE_CHECKING

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str

    # Ниже — ключ и алгоритм для JWT, такие же, как в Django
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.DATABASE_USER}:"  # noqa: E231
            f"{self.DATABASE_PASSWORD}@"
            f"{self.DATABASE_HOST}:"  # noqa: E231
            f"{self.DATABASE_PORT}/"
            f"{self.DATABASE_NAME}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings: "Settings"
if TYPE_CHECKING:  # ← для mypy
    settings = Settings(  # подставляем фиктивные данные
        DATABASE_USER="x",
        DATABASE_PASSWORD="x",
        DATABASE_HOST="x",
        DATABASE_PORT=5432,
        DATABASE_NAME="x",
        SECRET_KEY="dummy",
    )
else:
    settings = Settings()
