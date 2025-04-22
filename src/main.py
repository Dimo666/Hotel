from fastapi import FastAPI         # Импортируем FastAPI — основной класс для создания приложения
import uvicorn                      # Импортируем uvicorn — сервер, который запускает FastAPI-приложение

import sys # Для работы с путями
from pathlib import Path # Для работы с путями

sys.path.append(str(Path(__file__).parent.parent)) # Добавляем путь к корневому каталогу

from src.api.hotels import router as router_hotels # Импортируем роутер отелей
app = FastAPI()  # Создаём экземпляр FastAPI-приложения

# Подключаем роутер отелей к основному приложению
# Теперь все маршруты из hotels будут доступны по префиксу /hotels
app.include_router(router_hotels)

# Запуск приложения, если файл запущен напрямую
if __name__ == "__main__":
    # uvicorn запускает приложение с автоматическим перезапуском при изменении кода (reload=True)
    # "main:app" означает: искать объект `app` в файле `main.py`
    uvicorn.run("main:app", reload=True)