import logging
import redis.asyncio as redis


# Класс для управления асинхронным подключением к Redis
class RedisManager:
    def __init__(self, host: str, port: int):
        self.host = host  # Хост Redis-сервера
        self.port = port  # Порт Redis-сервера
        self.redis = None  # Объект подключения будет инициализирован позже

    # Установка соединения с Redis
    async def connect(self):
        logging.info(f"Connecting to Redis server -> host={self.host} port={self.port}")
        self.redis = await redis.Redis(host=self.host, port=self.port)
        logging.info(f"Connected to Redis server -> host={self.host} port={self.port}")

    # Установка значения по ключу с необязательным временем жизни (expire — в секундах)
    async def set(self, key: str, value: str, expire: int = None):
        if expire:
            await self.redis.set(key, value, ex=expire)
        else:
            await self.redis.set(key, value)

    # Получение значения по ключу
    async def get(self, key: str):
        return await self.redis.get(key)

    # Удаление ключа из Redis
    async def delete(self, key: str):
        await self.redis.delete(key)

    # Закрытие соединения с Redis
    async def close(self):
        if self.redis:
            await self.redis.close()


# Пример использования:
# redis_manager = RedisManager(host="localhost", port=6379)
# await redis_manager.connect()
# await redis_manager.set("key", "value", expire=60)
# value = await redis_manager.get("key")
# await redis_manager.delete("key")
# await redis_manager.close()
