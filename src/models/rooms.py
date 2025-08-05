import typing

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.database import Base

if typing.TYPE_CHECKING:
    from src.models import FacilitiesOrm


# ORM-модель комнаты (rooms)
class RoomsOrm(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)  # Уникальный ID комнаты
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))  # Внешний ключ на отель
    title: Mapped[str]  # Название комнаты
    description: Mapped[str | None]  # Описание (может быть пустым)
    price: Mapped[int]  # Цена за ночь
    quantity: Mapped[int]  # Количество таких комнат в отеле

    # Связь many-to-many с удобствами (facilities)
    facilities: Mapped[list["FacilitiesOrm"]] = relationship(
        back_populates="rooms",  # Обратная связь из FacilitiesOrm
        secondary="rooms_facilities",  # Промежуточная таблица
    )
