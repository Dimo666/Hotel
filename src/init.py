from src.config import settings  # Импорт настроек из .env (через класс Settings)
from src.connectors.redis_connector import RedisManager  # Класс-обёртка для работы с Redis


# Инициализация глобального Redis-менеджера для всего приложения

# Создаём экземпляр RedisManager, используя переменные окружения из .env
redis_manager = RedisManager(
    host=settings.REDIS_HOST,  # Хост Redis-сервера (например, "localhost")
    port=settings.REDIS_PORT,  # Порт Redis-сервера (например, 6379)
)
