# Импортируем базовую модель Pydantic и тип EmailStr для валидации email
from pydantic import BaseModel, ConfigDict, EmailStr


# Схема для запроса на регистрацию и логин
class UserRequestAdd(BaseModel):
    email: EmailStr  # Проверяет, что это валидный email
    password: str  # Пароль пользователя в открытом виде (от клиента)


# Схема для создания пользователя в базе данных
class UserAdd(BaseModel):
    email: EmailStr  # Email сохраняем как есть
    hashed_password: str  # Пароль уже должен быть захеширован!


# Схема для вывода пользователя (например, при получении данных)
class User(BaseModel):
    id: int  # ID пользователя из базы данных
    email: EmailStr  # Email пользователя

    # Это настройка Pydantic: позволяет создавать схему напрямую из ORM-объектов (из SQLAlchemy моделей)
    model_config = ConfigDict(from_attributes=True)


# Схема пользователя с захешированным паролем
# Наследуется от User, добавляя к нему поле hashed_password
class UserWithHashedPassword(User):
    hashed_password: str  # Хеш пароля (используется только внутри системы)
