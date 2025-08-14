import typing

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.database import Base

if typing.TYPE_CHECKING:
    from src.models import FacilitiesOrm  # Для аннотаций, чтобы избежать циклического импорта


class RoomsOrm(Base):
    """
    ORM-модель таблицы 'rooms' — представляет номера (комнаты) в отелях.

    Каждая комната принадлежит одному отелю и может быть связана с несколькими удобствами (many-to-many).
    """

    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)  # Уникальный идентификатор комнаты
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))  # Внешний ключ на таблицу отелей
    title: Mapped[str]  # Название комнаты (например, "Standard", "Deluxe Suite")
    description: Mapped[str | None]  # Описание комнаты (опционально)
    price: Mapped[int]  # Цена за одну ночь
    quantity: Mapped[int]  # Количество таких комнат в отеле

    # Связь many-to-many с удобствами (facilities)
    facilities: Mapped[list["FacilitiesOrm"]] = relationship(
        back_populates="rooms",  # Обратная связь из FacilitiesOrm.rooms
        secondary="rooms_facilities",  # Промежуточная таблица связи
    )
