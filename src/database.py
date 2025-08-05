from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.config import settings  # Настройки проекта (включая DB_URL из .env)


# 🔧 Создаём асинхронный движок SQLAlchemy (с пулом соединений по умолчанию)
engine = create_async_engine(settings.DB_URL)

# 🔧 Движок без пула соединений (используется для миграций, Alembic, фоновых задач)
engine_null_pool = create_async_engine(settings.DB_URL, poolclass=NullPool)


# 🏭 Асинхронная фабрика сессий, привязанная к основному движку
# expire_on_commit=False — после commit() объекты останутся доступными в памяти
async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

# 🏭 Фабрика сессий для работы без пула соединений (используется в Alembic и тестах)
async_session_maker_null_pool = async_sessionmaker(
    bind=engine_null_pool,
    expire_on_commit=False,
)


# 🧱 Базовый класс для всех ORM-моделей
# Все модели должны наследоваться от Base, чтобы быть видимыми для Alembic
class Base(DeclarativeBase):
    """
    Базовый класс для всех ORM-моделей проекта.
    Используется для генерации таблиц и миграций.
    """
    pass
