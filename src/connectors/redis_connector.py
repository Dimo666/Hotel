import logging
import redis.asyncio as redis


class RedisManager:
    """
    Класс для управления асинхронным подключением к Redis.

    Позволяет:
    - устанавливать соединение
    - устанавливать/получать/удалять ключи
    - закрывать соединение
    """

    def __init__(self, host: str, port: int):
        """
        Инициализация параметров подключения.

        :param host: адрес Redis-сервера
        :param port: порт Redis-сервера
        """
        self.host = host
        self.port = port
        self.redis = None  # Объект Redis будет создан при connect()

    async def connect(self):
        """
        Подключение к Redis.

        Создаёт асинхронный клиент Redis и логирует событие.
        """
        logging.info(f"Connecting to Redis server -> host={self.host} port={self.port}")
        self.redis = await redis.Redis(host=self.host, port=self.port)
        logging.info(f"Connected to Redis server -> host={self.host} port={self.port}")

    async def set(self, key: str, value: str, expire: int = None):
        """
        Установка значения по ключу.

        :param key: ключ в Redis
        :param value: строковое значение
        :param expire: время жизни ключа в секундах (опционально)
        """
        if expire:
            await self.redis.set(key, value, ex=expire)
        else:
            await self.redis.set(key, value)

    async def get(self, key: str):
        """
        Получение значения по ключу.

        :param key: ключ
        :return: значение (или None, если ключа нет)
        """
        return await self.redis.get(key)

    async def delete(self, key: str):
        """
        Удаление ключа из Redis.

        :param key: ключ
        """
        await self.redis.delete(key)

    async def close(self):
        """
        Закрытие подключения к Redis.
        """
        if self.redis:
            await self.redis.close()


# Пример использования:
# redis_manager = RedisManager(host="localhost", port=6379)
# await redis_manager.connect()
# await redis_manager.set("key", "value", expire=60)
# value = await redis_manager.get("key")
# await redis_manager.delete("key")
# await redis_manager.close()
