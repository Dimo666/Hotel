from pydantic_settings import BaseSettings, SettingsConfigDict  # Импорт базового класса для работы с .env файлами

# Класс для загрузки и хранения настроек из .env файла
class Settings(BaseSettings):
    DB_HOST: str   # Хост базы данных (например, localhost)
    DB_PORT: int   # Порт (например, 5432)
    DB_USER: str   # Имя пользователя БД
    DB_PASS: str   # Пароль
    DB_NAME: str   # Название базы данных

    REDIS_HOST: str
    REDIS_PORT: int

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property  # Декоратор, превращает метод в свойство
    def DB_URL(self) -> str:
        # Собираем URL для подключения к PostgreSQL через asyncpg
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Указываем, откуда брать переменные окружения (.env)
    model_config = SettingsConfigDict(env_file=".env")

# Создаём экземпляр настроек, данные подтянутся из .env
settings = Settings()
