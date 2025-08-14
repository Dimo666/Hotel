from datetime import date
from sqlalchemy import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property  # Позволяет использовать свойство и в Python, и в SQL
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base  # Базовый класс для всех ORM-моделей


class BookingsOrm(Base):
    """
    ORM-модель таблицы 'bookings' — хранит информацию о бронированиях комнат пользователями.
    """

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)  # Уникальный ID бронирования
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # Связь с пользователем (внешний ключ)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))  # Связь с комнатой (внешний ключ)
    date_from: Mapped[date]  # Дата заезда
    date_to: Mapped[date]  # Дата выезда
    price: Mapped[int]  # Цена за одну ночь

    @hybrid_property
    def total_cost(self) -> int:
        """
        Гибридное свойство — считает полную стоимость бронирования на стороне Python.

        Может использоваться и как обычное поле (в Python),
        и как часть SQL-запросов (если реализовать .expression).
        """
        return self.price * (self.date_to - self.date_from).days
