from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from src.database import Base


class HotelsOrm(Base):
    """
    ORM-модель таблицы 'hotels' — представляет отели в системе.

    Примеры: Hilton, Radisson, Plaza Inn и т.п.
    """
    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(primary_key=True)  # Уникальный ID отеля
    title: Mapped[str] = mapped_column(String(100))  # Название отеля (до 100 символов)
    location: Mapped[str] = mapped_column(String(100))  # Локация или slug (например, 'paris' или 'new-york')
