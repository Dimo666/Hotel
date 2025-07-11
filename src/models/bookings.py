from datetime import date
from sqlalchemy import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property  # Позволяет использовать свойство и в Python, и в SQL
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base  # Базовый класс для моделей


# ORM-модель для таблицы "bookings"
class BookingsOrm(Base):
    __tablename__ = 'bookings'

    id: Mapped[int] = mapped_column(primary_key=True)  # Первичный ключ
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))  # Внешний ключ на таблицу users
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id'))  # Внешний ключ на таблицу rooms
    date_from: Mapped[date]  # Дата заезда
    date_to: Mapped[date]    # Дата выезда
    price: Mapped[int]       # Цена за ночь

    @hybrid_property
    def total_cost(self) -> int:
        # Вычисляет общую стоимость бронирования
        return self.price * (self.date_to - self.date_from).days
