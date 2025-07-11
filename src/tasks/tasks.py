import asyncio
from time import sleep
from PIL import Image  # Библиотека для работы с изображениями
import os

from src.database import async_session_maker_null_pool  # Асинхронный сессионный фабрикатор без пула
from src.tasks.celery_app import celery_instance  # Экземпляр Celery
from src.utils.db_manager import DBManager  # Менеджер работы с БД

# Простейшая задача для теста — "успать" и вывести сообщение
@celery_instance.task
def test_tasks():
    sleep(5)
    print("Я МОЛОДЕЦ")


# Задача: изменить размер изображения до нескольких ширин
@celery_instance.task
def resize_image(image_path: str):
    sizes = [1000, 500, 200]  # Целевые ширины
    output_folder = 'src/static/images'  # Папка для сохранения

    img = Image.open(image_path)  # Открываем исходное изображение

    # Извлекаем имя файла и расширение
    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)

    for size in sizes:
        # Подсчитываем пропорциональную высоту и сжимаем изображение
        img_resized = img.resize((size, int(img.height * (size / img.width))), Image.Resampling.LANCZOS)

        # Генерируем новое имя файла
        new_file_name = f"{name}_{size}px{ext}"
        output_path = os.path.join(output_folder, new_file_name)

        # Сохраняем
        img_resized.save(output_path)

    print(f"Изображение сохранено в следующих размерах: {sizes} в папке {output_folder}")


# Асинхронный помощник — получает бронирования с заездом на сегодня
async def get_bookings_with_today_checkin_helper():
    print("Я ЗАПУСКАЮСЬ")
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        bookings = await db.bookings.get_bookings_with_today_checkin()
        print(f"{bookings=}")


# Обёртка Celery для вызова асинхронной функции через asyncio.run
@celery_instance.task(name="booking_today_checkin")
def send_emails_to_users_with_today_checkin():
    asyncio.run(get_bookings_with_today_checkin_helper())
