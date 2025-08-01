import json
from unittest import mock

# Отключаем кэширование в тестах, подменяя декоратор fastapi_cache.decorator.cache на пустой
# lambda-декоратор, который просто возвращает оригинальную функцию без изменений.
# Это нужно, чтобы кэш не влиял на поведение и результаты тестов.
mock.patch(
    "fastapi_cache.decorator.cache",  # Импортируемый путь к декоратору, который нужно замокать
    lambda *args, **kwargs: lambda f: f  # Подмена: декоратор ничего не делает и возвращает исходную функцию
).start()  # Активируем патч сразу при импорте


import pytest
from httpx import AsyncClient


# Зависимость для получения сессии БД
from src.api.dependencies import get_db
# Настройки проекта, включая переменную окружения MODE
from src.config import settings
# SQLAlchemy: базовая модель и движок без connection pool (NullPool используется для тестов)
from src.database import Base, engine_null_pool, async_session_maker_null_pool
# Импорт приложения FastAPI
from src.main import app
# Импорт всех моделей (чтобы Base.metadata знала о всех таблицах)
from src.models import *
# Схемы для отелей и номеров
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
# Утилита для работы с базой через репозитории
from src.utils.db_manager import DBManager


# ⛔ Фикстура проверки окружения (тесты можно запускать только если MODE=TEST)
@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


# 📦 Фикстура для переопределения зависимости get_db, чтобы использовать тестовый движок
async def get_db_null_pool():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db


# 📦 Фикстура для получения менеджера БД в отдельных тестах
@pytest.fixture(scope="function")
async def db() -> DBManager:
    async for db in get_db_null_pool():
        yield db


# ⛓️ Переопределяем зависимость get_db на тестовую версию
app.dependency_overrides[get_db] = get_db_null_pool


# 🛠️ Фикстура инициализации БД:
# - удаляет все таблицы,
# - создаёт заново структуру БД,
# - заполняет тестовыми данными из JSON
@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)   # Удаляем все таблицы
        await conn.run_sync(Base.metadata.create_all) # Создаём заново таблицы

    # Загружаем тестовые данные
    with open("tests/mock_hotels.json", encoding="utf-8") as file_hotels:
        hotels = json.load(file_hotels)
    with open("tests/mock_rooms.json", encoding="utf-8") as file_rooms:
        rooms = json.load(file_rooms)

    # Преобразуем словари в Pydantic-схемы
    hotels = [HotelAdd.model_validate(hotel) for hotel in hotels]
    rooms = [RoomAdd.model_validate(room) for room in rooms]

    # Добавляем тестовые записи в базу
    async with DBManager(session_factory=async_session_maker_null_pool) as db_:
        await db_.hotels.add_bulk(hotels)
        await db_.rooms.add_bulk(rooms)
        await db_.commit()


# 🌐 Фикстура HTTP-клиента для работы с API через httpx
@pytest.fixture(scope="session")
async def ac() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# 🔐 Фикстура регистрации тестового пользователя
# Используется перед тестами, где нужна авторизация
@pytest.fixture(scope="session", autouse=True)
async def register_user(ac, setup_database):
    await ac.post(
        "/auth/register",
        json={
            "email": "kot@pes.com",
            "password": "1234"
        }
    )

@pytest.fixture(scope="session")
async def authenticated_ac(ac: AsyncClient, register_user) -> AsyncClient:
    # Выполняем вход: получаем access_token
    response = await ac.post(
        "/auth/login",
        json={
            "email": "kot@pes.com",
            "password": "1234"
        }
    )
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    # Добавляем токен в заголовки клиента
    ac.headers.update({"Authorization": f"Bearer {access_token}"})

    yield ac
