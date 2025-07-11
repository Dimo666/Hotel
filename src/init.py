from src.config import settings  # Импорт настроек из .env (через класс Settings)
from src.connectors.redis_connector import RedisManager  # Класс-обёртка для работы с Redis

# Создаём экземпляр RedisManager с хостом и портом из настроек
redis_manager = RedisManager(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
)
