import typing
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from src.database import Base


if typing.TYPE_CHECKING:
    from src.models import RoomsOrm

# Модель удобства (удобства, которые можно выбрать в комнате)
class FacilitiesOrm(Base):
    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(primary_key=True)  # Уникальный ID удобства
    title: Mapped[str] = mapped_column(String(100))    # Название удобства (до 100 символов)

    # Связь many-to-many с комнатами
    rooms: Mapped[list["RoomsOrm"]] = relationship(
        back_populates="facilities",        # Обратная связь из RoomsOrm
        secondary="rooms_facilities",       # Промежуточная таблица
    )


# Промежуточная таблица для связи rooms <-> facilities (many-to-many)
class RoomsFacilitiesOrm(Base):
    __tablename__ = "rooms_facilities"

    id: Mapped[int] = mapped_column(primary_key=True)  # ID связи
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))  # ID комнаты
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))  # ID удобства
