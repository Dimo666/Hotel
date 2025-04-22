from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # Импорт асинхронных инструментов SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from src.config import settings  # Импорт настроек из config.py, где настроен доступ к .env

# Создаём асинхронный движок SQLAlchemy с использованием строки подключения из .env
engine = create_async_engine(settings.DB_URL)


# Создаём асинхронную фабрику сессий
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


# Определяем базовый класс для моделей
class Base(DeclarativeBase):
    pass