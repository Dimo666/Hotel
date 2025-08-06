from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Класс для загрузки и хранения настроек из .env файла.

    Используется для управления конфигурацией приложения (БД, Redis, JWT и т.д.).
    Все значения автоматически подтягиваются из переменных окружения.
    """

    # ▶️ Режим запуска приложения
    MODE: Literal["TEST", "LOCAL", "DEV", "PROD"]

    # 📦 Параметры подключения к PostgreSQL
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    # ⚡ Параметры подключения к Redis
    REDIS_HOST: str
    REDIS_PORT: int

    @property
    def REDIS_URL(self) -> str:
        """
        Сформированный URL подключения к Redis.
        """
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def DB_URL(self) -> str:
        """
        Сформированный URL подключения к PostgreSQL (через asyncpg).
        Используется в create_async_engine().
        """
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # 🔐 JWT-настройки
    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int  # Время жизни токена в минутах

    # 📄 Загрузка переменных из файла .env в корне проекта
    model_config = SettingsConfigDict(env_file=".env")


# 📌 Глобальный доступ к настройкам проекта
settings = Settings()
