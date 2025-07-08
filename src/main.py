from contextlib import asynccontextmanager
from fastapi import FastAPI         # Импортируем FastAPI — основной класс для создания приложения
import uvicorn                      # Импортируем uvicorn — сервер, который запускает FastAPI-приложение

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend


import sys                          # Для работы с путями
from pathlib import Path            # Для работы с путями


sys.path.append(str(Path(__file__).parent.parent)) # Добавляем путь к корневому каталогу


from src.init import redis_manager

from src.api.hotels import router as router_hotels # Импортируем роутер отелей
from src.api.auth import router as router_auth
from src.api.rooms import router as router_rooms
from src.api.bookings import router as router_bookings
from src.api.facilities import router as router_facilities

@asynccontextmanager
async def lifespan(app: FastAPI):
    # При старте проекта
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    yield
    # При выключени/перезагрузке приложения
    await redis_manager.close()

app = FastAPI(lifespan=lifespan)  # Создаём экземпляр FastAPI-приложения

# Подключаем роутер отелей к основному приложению

app.include_router(router_auth)
# Теперь все маршруты из hotels будут доступны по префиксу /hotels
app.include_router(router_hotels)

app.include_router(router_rooms)

app.include_router(router_bookings)

app.include_router(router_facilities)


# Запуск приложения, если файл запущен напрямую
if __name__ == "__main__":
    # uvicorn запускает приложение с автоматическим перезапуском при изменении кода (reload=True)
    # "main:app" означает: искать объект `app` в файле `main.py`
    uvicorn.run("main:app", reload=True)