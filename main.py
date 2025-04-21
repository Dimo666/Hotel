from fastapi import FastAPI         # Импортируем FastAPI — основной класс для создания приложения
import uvicorn                      # Импортируем uvicorn — сервер, который запускает FastAPI-приложение
from hotels import router as router_hotels  # Импортируем роутер из модуля hotels и даём ему короткое имя

app = FastAPI()  # Создаём экземпляр FastAPI-приложения

# Подключаем роутер отелей к основному приложению
# Теперь все маршруты из hotels будут доступны по префиксу /hotels
app.include_router(router_hotels)

# Запуск приложения, если файл запущен напрямую
if __name__ == "__main__":
    # uvicorn запускает приложение с автоматическим перезапуском при изменении кода (reload=True)
    # "main:app" означает: искать объект `app` в файле `main.py`
    uvicorn.run("main:app", reload=True)