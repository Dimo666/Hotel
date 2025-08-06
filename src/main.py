from contextlib import asynccontextmanager
from fastapi import FastAPI  # Основной класс FastAPI-приложения
import uvicorn  # ASGI-сервер для запуска приложения

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend  # Бэкенд кэша через Redis

import logging
import sys
from pathlib import Path

# Добавляем корневую директорию в sys.path для корректного импорта модулей
sys.path.append(str(Path(__file__).parent.parent))

# Настройка логирования на уровне DEBUG
logging.basicConfig(level=logging.DEBUG)

from src.init import redis_manager  # Инициализация Redis-соединения

# Импорт API-роутеров
from src.api.hotels import router as router_hotels
from src.api.auth import router as router_auth
from src.api.rooms import router as router_rooms
from src.api.bookings import router as router_bookings
from src.api.facilities import router as router_facilities
from src.api.images import router as router_images


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекст жизненного цикла приложения FastAPI.
    Выполняется при старте и остановке сервера.

    - Подключение к Redis
    - Инициализация кэша FastAPI
    - Отключение от Redis при завершении
    """
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    logging.info("FastAPI cache initialized")
    yield
    await redis_manager.close()


# Создание экземпляра FastAPI с lifespan-контекстом
app = FastAPI(lifespan=lifespan)

# Подключение роутеров (эндпоинтов)
app.include_router(router_auth)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_bookings)
app.include_router(router_facilities)
app.include_router(router_images)


# Точка входа при запуске через `python main.py`
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)  # reload=True — автообновление при изменении кода
