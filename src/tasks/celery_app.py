from celery import Celery
from src.config import (
    settings,
)  # Импорт настроек (где хранится REDIS_URL и другие переменные окружения)

# Создание экземпляра Celery
# "tasks" — имя приложения Celery
# broker — URL брокера сообщений (в данном случае Redis)
# include — список модулей, в которых Celery будет искать задачи
celery_instance = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    include=[
        "src.tasks.tasks",  # Путь к модулю, где определены задачи Celery
    ],
)

# Конфигурация планировщика задач (beat)
# beat_schedule — словарь периодических задач
celery_instance.conf.beat_schedule = {
    "luboe-nazvanie": {  # Уникальное имя задачи
        "task": "booking_today_checkin",  # Имя задачи (должно совпадать с @celery.task(name=...)
        "schedule": 5,  # Интервал в секундах (например, каждые 5 секунд)
    }
}
