from typing import Literal
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)  # Базовый класс и конфиг для загрузки переменных из .env


# Класс для загрузки и хранения настроек из .env файла
class Settings(BaseSettings):
    MODE: Literal["TEST", "LOCAL", "DEV", "PROD"]  # Среда запуска приложения

    DB_HOST: str  # Хост базы данных
    DB_PORT: int  # Порт PostgreSQL
    DB_USER: str  # Пользователь PostgreSQL
    DB_PASS: str  # Пароль PostgreSQL
    DB_NAME: str  # Название базы данных

    REDIS_HOST: str  # Хост Redis
    REDIS_PORT: int  # Порт Redis

    @property
    def REDIS_URL(self) -> str:
        # Собираем URL подключения к Redis
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def DB_URL(self) -> str:
        # Собираем строку подключения к PostgreSQL через asyncpg
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    JWT_SECRET_KEY: str  # Секретный ключ для подписи JWT токенов
    ALGORITHM: str  # Алгоритм подписи JWT (например, HS256)
    ACCESS_TOKEN_EXPIRE_MINUTES: int  # Время жизни access-токена в минутах

    # Указываем, что настройки будут загружены из .env файла
    model_config = SettingsConfigDict(env_file=".env")


# Создаём глобальный экземпляр настроек
settings = Settings()
