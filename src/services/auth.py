# Импортируем библиотеку для работы с JWT токенами
import jwt

# Контекст для безопасного хеширования паролей
from passlib.context import CryptContext

# Работа с датой и временем
from datetime import datetime, timezone, timedelta

# Настройки проекта (секретный ключ, алгоритм, TTL токенов)
from src.config import settings
from src.exceptions import IncorrectPasswordException, EmailNotRegisteredException, ObjectAlreadyExistsException, UserAlreadyExistsException
from src.schemas.users import UserRequestAdd, UserAdd
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
            raise IncorrectPasswordException

    async def login_user(self, data: UserRequestAdd):
        user = await self.db.users.get_user_with_hashed_password(email=data.email)
        if not user:
            raise EmailNotRegisteredException

        if not AuthService().verify_password(data.password, user.hashed_password):
            raise IncorrectPasswordException

        access_token = AuthService().create_access_token({"user_id": user.id})
        return access_token

    async def register_user(self, data: UserRequestAdd):
        hashed_password = self.hash_password(data.password)
        new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
        try:
            await self.db.users.add(new_user_data)
            await self.db.commit()
        except ObjectAlreadyExistsException as ex:
            raise UserAlreadyExistsException from ex

    async def get_one_or_none(self, user_id: int):
        return await self.db.users.get_one_or_none(id=user_id)
