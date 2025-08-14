# ruff: noqa: E402 — отключаем проверку порядка импортов
import json
from unittest import mock

# 🚫 Отключаем кэширование в тестах
# Заменяем декоратор @cache на пустую обёртку, чтобы кэш не мешал тестам
mock.patch(
    "fastapi_cache.decorator.cache",
    lambda *args, **kwargs: lambda f: f
).start()


import pytest
from httpx import AsyncClient

# ⛓️ Зависимости и база
from src.api.dependencies import get_db
from src.config import settings
from src.database import Base, engine_null_pool, async_session_maker_null_pool
from src.main import app
from src.models import *  # noqa: F403
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.utils.db_manager import DBManager


# ✅ Проверка окружения — тесты запускаются только в режиме TEST
@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    """
    Проверка, что тесты запускаются только в окружении TEST.
    """
    assert settings.MODE == "TEST", "Тесты можно запускать только в окружении MODE=TEST"


# 🧪 Переопределяем зависимость get_db для тестов (используем отдельный движок без пула)
async def get_db_null_pool():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db


# 💾 Фикстура: менеджер базы данных для использования в тестах напрямую
@pytest.fixture(scope="function")
async def db() -> DBManager:
    """
    Предоставляет доступ к тестовой БД внутри отдельных тестов.
    """
    async for db in get_db_null_pool():
        yield db


# 🔁 Переопределение зависимости get_db внутри FastAPI на тестовую версию
app.dependency_overrides[get_db] = get_db_null_pool


# 🧱 Инициализация базы данных (удаление всех таблиц, создание, наполнение данными)
@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    """
    Полная инициализация тестовой базы данных:
    - Очистка и пересоздание всех таблиц
    - Наполнение данными из JSON-файлов
    """
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    with open("tests/mock_hotels.json", encoding="utf-8") as file_hotels:
        hotels = json.load(file_hotels)
    with open("tests/mock_rooms.json", encoding="utf-8") as file_rooms:
        rooms = json.load(file_rooms)

    hotels = [HotelAdd.model_validate(h) for h in hotels]
    rooms = [RoomAdd.model_validate(r) for r in rooms]

    async with DBManager(session_factory=async_session_maker_null_pool) as db_:
        await db_.hotels.add_bulk(hotels)
        await db_.rooms.add_bulk(rooms)
        await db_.commit()


# 🌐 HTTP-клиент для вызова API (httpx имитирует запросы к FastAPI-приложению)
@pytest.fixture(scope="session")
async def ac() -> AsyncClient:
    """
    HTTP-клиент без авторизации (используется для public ручек).
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# 🔐 Регистрация пользователя (используется в начале сессии)
@pytest.fixture(scope="session", autouse=True)
async def register_user(ac, setup_database):
    """
    Регистрирует тестового пользователя один раз за сессию.
    Используется для тестов, где требуется логин.
    """
    await ac.post(
        "/auth/register",
        json={"email": "kot@pes.com", "password": "1234"}
    )


# ✅ Аутентифицированный клиент (после логина)
@pytest.fixture(scope="session")
async def authenticated_ac(register_user, ac):
    """
    Возвращает httpx-клиент с access_token в cookies.

    Используется в тестах, где требуется авторизация.
    """
    await ac.post(
        "/auth/login",
        json={"email": "kot@pes.com", "password": "1234"}
    )

    assert ac.cookies["access_token"], "Access token не установлен после логина"

    yield ac  # Возвращаем клиент с авторизацией
