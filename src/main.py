from contextlib import asynccontextmanager
from fastapi import FastAPI  # Основной класс для FastAPI-приложения
import uvicorn  # ASGI-сервер для запуска приложения

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend  # Кеширование через Redis

import sys
from pathlib import Path

# Добавляем корневую папку в sys.path для корректного импорта
sys.path.append(str(Path(__file__).parent.parent))

from src.init import redis_manager  # Инициализация Redis-соединения

# Импортируем роутеры API
from src.api.hotels import router as router_hotels
from src.api.auth import router as router_auth
from src.api.rooms import router as router_rooms
from src.api.bookings import router as router_bookings
from src.api.facilities import router as router_facilities
from src.api.images import router as router_images


# lifespan — асинхронный контекст, выполняется при старте и завершении приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()  # Подключение к Redis
    FastAPICache.init(
        RedisBackend(redis_manager.redis), prefix="fastapi-cache"
    )  # Инициализация кеша
    yield
    await redis_manager.close()  # Отключение от Redis при завершении


# Создаём FastAPI-приложение с lifespan
app = FastAPI(lifespan=lifespan)

# Подключаем все роутеры
app.include_router(router_auth)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_bookings)
app.include_router(router_facilities)
app.include_router(router_images)

# Точка входа для запуска через python main.py
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)  # reload=True — перезапуск при изменении кода
