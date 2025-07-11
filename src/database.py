from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # Импорт асинхронных инструментов SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from src.config import settings  # Импорт настроек из config.py, где настроен доступ к .env

# Создаём асинхронный движок SQLAlchemy с использованием строки подключения из .env
engine = create_async_engine(settings.DB_URL)  # Движок с дефолтным пулом соединений

# Создаём движок без пула соединений (например, для миграций или однократных задач)
engine_null_pool = create_async_engine(settings.DB_URL, poolclass=NullPool)

# Создаём асинхронную фабрику сессий, привязанную к основному движку
# expire_on_commit=False означает, что данные останутся доступными после commit()
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

# Фабрика сессий, использующая движок без пула (например, для Alembic)
async_session_maker_null_pool = async_sessionmaker(bind=engine_null_pool, expire_on_commit=False)

# Базовый класс для всех ORM-моделей
# Все модели должны наследоваться от этого класса
class Base(DeclarativeBase):
    pass
