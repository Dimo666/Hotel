# Импортируем библиотеку для работы с JWT токенами
import jwt

# Импортируем контекст для безопасного хеширования паролей
from passlib.context import CryptContext

# Импортируем модули для работы с датой и временем
from datetime import datetime, timezone, timedelta

# Импортируем настройки проекта (секреты, время жизни токенов и т.д.)
from src.config import settings


# Сервис для работы с аутентификацией
class AuthService:
    # Контекст для работы с паролями через bcrypt
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Метод для создания JWT access-токена
    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()  # Делаем копию переданного словаря (чтобы не изменять оригинал)
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        # Добавляем в данные срок жизни токена (ключ "exp")
        to_encode.update({"exp": expire})
        # Кодируем токен с использованием секретного ключа и алгоритма
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    # Метод для хеширования пароля
    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    # Метод для проверки пароля: сравнивает обычный и захешированный пароли
    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)
