from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from src.database import Base


class UsersOrm(Base):
    """
    ORM-модель таблицы 'users' — представляет пользователей системы.

    Используется для авторизации, регистрации и хранения учётных данных.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)  # Уникальный идентификатор пользователя
    email: Mapped[str] = mapped_column(String(200), unique=True)  # Email пользователя (уникальный, до 200 символов)
    hashed_password: Mapped[str] = mapped_column(String(255))  # Захешированный пароль (до 255 символов)
