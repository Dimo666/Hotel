import pytest

from src.config import settings  # Настройки проекта (в том числе MODE)
from src.database import Base, engine_null_pool  # Base — базовый класс моделей, engine — движок без пула
from src.models import *  # Импорт всех моделей (обязательно, чтобы они были зарегистрированы в Base.metadata)


# Фикстура выполняется один раз на всю тестовую сессию
# Используется для инициализации чистой тестовой БД
@pytest.fixture(scope="session", autouse=True)
async def async_main():
    print("Я ФИКСТУРА")

    # Проверка безопасности — запускаем только в тестовом режиме
    assert settings.MODE == "TEST"

    # Асинхронное подключение к БД и пересоздание всех таблиц
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Удаляем все таблицы
        await conn.run_sync(Base.metadata.create_all)  # Создаём заново (чистая БД)
