from fastapi import FastAPI         # Импортируем FastAPI — основной класс для создания приложения
import uvicorn                      # Импортируем uvicorn — сервер, который запускает FastAPI-приложение
import sys                          # Для работы с путями
from pathlib import Path            # Для работы с путями

sys.path.append(str(Path(__file__).parent.parent)) # Добавляем путь к корневому каталогу

from src.api.hotels import router as router_hotels # Импортируем роутер отелей
from src.api.auth import router as router_auth
from src.api.rooms import router as router_rooms
app = FastAPI()  # Создаём экземпляр FastAPI-приложения

# Подключаем роутер отелей к основному приложению

app.include_router(router_auth)
# Теперь все маршруты из hotels будут доступны по префиксу /hotels
app.include_router(router_hotels)

app.include_router(router_rooms)


# Запуск приложения, если файл запущен напрямую
if __name__ == "__main__":
    # uvicorn запускает приложение с автоматическим перезапуском при изменении кода (reload=True)
    # "main:app" означает: искать объект `app` в файле `main.py`
    uvicorn.run("main:app", reload=True)