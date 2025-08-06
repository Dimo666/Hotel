from pydantic import BaseModel, ConfigDict, EmailStr


class UserRequestAdd(BaseModel):
    """
    Схема запроса от клиента для регистрации или авторизации.

    Используется в POST /auth/register и POST /auth/login.
    """
    email: EmailStr  # Валидный email (валидируется автоматически)
    password: str  # Открытый пароль, который будет захеширован


class UserAdd(BaseModel):
    """
    Схема для создания пользователя в базе данных.

    Используется внутри бизнес-логики, когда пароль уже захеширован.
    """
    email: EmailStr
    hashed_password: str  # Пароль, прошедший хеширование


class User(BaseModel):
    """
    Схема для возврата данных о пользователе (например, в /auth/me).

    Без пароля.
    """
    id: int  # Уникальный идентификатор пользователя
    email: EmailStr  # Email пользователя

    model_config = ConfigDict(from_attributes=True)  # Поддержка ORM-моделей (SQLAlchemy → Pydantic)


class UserWithHashedPassword(User):
    """
    Расширенная схема пользователя, включающая хеш пароля.

    Используется только внутри системы, не возвращается клиенту.
    """
    hashed_password: str
