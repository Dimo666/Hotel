import json
import pytest
from sqlalchemy import insert
from httpx import AsyncClient

# Настройки проекта (в том числе переменная окружения MODE)
from src.config import settings

# SQLAlchemy: базовый класс моделей и движок без connection pool (NullPool для тестов)
from src.database import Base, engine_null_pool, async_session_maker_null_pool

# Импорт приложения FastAPI
from src.main import app

# Импорт всех моделей, чтобы Base.metadata увидела все таблицы
from src.models import *
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.utils.db_manager import DBManager


# ⛔ Защита: тесты можно запускать только если MODE=TEST
@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


@pytest.fixture(scope="function")
async def db() -> DBManager:
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db


# 🛠 Фикстура инициализации БД: удаляет и создаёт таблицы, загружает тестовые данные
@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    # Подключаемся к базе данных без connection pool (NullPool подходит для тестов)
    async with engine_null_pool.begin() as conn:
        # Удаляем все таблицы перед тестами (гарантированно чистая база)
        await conn.run_sync(Base.metadata.drop_all)
        # Создаём заново все таблицы, чтобы работать с актуальной схемой
        await conn.run_sync(Base.metadata.create_all)

    # Загружаем фикстурные (тестовые) данные из JSON-файлов
    with open("tests/mock_hotels.json", encoding="utf-8") as file_hotels:
        hotels = json.load(file_hotels)
    with open("tests/mock_rooms.json", encoding="utf-8") as file_rooms:
        rooms = json.load(file_rooms)

    # Валидируем и превращаем словари в Pydantic-модели HotelAdd и RoomAdd
    hotels = [HotelAdd.model_validate(hotel) for hotel in hotels]
    rooms = [RoomAdd.model_validate(room) for room in rooms]

    # Через менеджер БД добавляем тестовые данные в таблицы
    async with DBManager(session_factory=async_session_maker_null_pool) as db_:
        await db_.hotels.add_bulk(hotels)  # Массово добавляем отели
        await db_.rooms.add_bulk(rooms)    # Массово добавляем номера
        await db_.commit()  # Подтверждаем изменения


@pytest.fixture(scope="session")
async def ac() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# 🔐 Фикстура регистрации пользователя через эндпоинт /auth/register
# Выполняется после инициализации БД
@pytest.fixture(scope="session", autouse=True)
async def register_user(ac, setup_database):
    await ac.post(
        "/auth/register",
        json={
            "email": "kot@pes.com",
            "password": "1234"
        }
    )
