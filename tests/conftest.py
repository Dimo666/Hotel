import json
import pytest
from sqlalchemy import insert
from httpx import AsyncClient

# Настройки проекта (в том числе переменная окружения MODE)
from src.config import settings

# SQLAlchemy: базовый класс моделей и движок без connection pool (NullPool для тестов)
from src.database import Base, engine_null_pool

# Импорт приложения FastAPI
from src.main import app

# Импорт всех моделей, чтобы Base.metadata увидела все таблицы
from src.models import *

# Импорт конкретных моделей для вставки данных
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm


# ⛔ Защита: тесты можно запускать только если MODE=TEST
@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


# 🛠 Фикстура инициализации БД: удаляет и создаёт таблицы, загружает тестовые данные
@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with engine_null_pool.begin() as conn:
        # Удаляем все таблицы перед тестами (гарантированно чистая база)
        await conn.run_sync(Base.metadata.drop_all)

        # Создаём заново все таблицы
        await conn.run_sync(Base.metadata.create_all)

        # 📥 Загружаем данные из mock_hotels.json и вставляем в таблицу hotels
        with open("tests/mock_hotels.json", encoding="utf-8") as f:
            hotels_data = json.load(f)
        await conn.execute(insert(HotelsOrm), hotels_data)

        # 📥 Загружаем данные из mock_rooms.json и вставляем в таблицу rooms
        with open("tests/mock_rooms.json", encoding="utf-8") as f:
            rooms_data = json.load(f)
        await conn.execute(insert(RoomsOrm), rooms_data)


# 🔐 Фикстура регистрации пользователя через эндпоинт /auth/register
# Выполняется после инициализации БД
@pytest.fixture(scope="session", autouse=True)
async def register_user(setup_database):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post(
            "/auth/register",
            json={
                "email": "kot@pes.com",
                "password": "1234"
            }
        )
