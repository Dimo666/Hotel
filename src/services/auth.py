# Импортируем библиотеку для работы с JWT токенами
import jwt
from fastapi import HTTPException

# Контекст для безопасного хеширования паролей
from passlib.context import CryptContext

# Работа с датой и временем
from datetime import datetime, timezone, timedelta

# Настройки проекта (секретный ключ, алгоритм, TTL токенов)
from src.config import settings
from src.services.base import BaseService


class AuthService(BaseService):
    """
    Сервис для работы с аутентификацией:
    - создание и декодирование JWT токенов
    - хеширование и проверка паролей
    """

    # Контекст хеширования паролей через bcrypt
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(self, data: dict) -> str:
        """
        Генерация access-токена с истечением срока действия.

        :param data: данные для кодирования (например: {"user_id": 123})
        :return: JWT токен (строка)
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})

        # Создаём токен с помощью секретного ключа и алгоритма (HS256, RS256 и т.д.)
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def hash_password(self, password: str) -> str:
        """
        Хеширование пароля с использованием bcrypt.

        :param password: обычный текстовый пароль
        :return: захешированный пароль
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Проверка пароля: сравнивает введённый и сохранённый хеш.

        :param plain_password: оригинальный пароль
        :param hashed_password: хеш из базы данных
        :return: True, если пароли совпадают
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def decode_token(self, token: str) -> dict:
        """
        Декодирует JWT токен и возвращает payload (например, {"user_id": 123}).

        :param token: JWT access token
        :raises HTTPException: если токен недействителен или повреждён
        :return: словарь с данными из токена
        """
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=401, detail="Неверный токен")
