import typing
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from src.database import Base  # Базовый класс всех моделей

if typing.TYPE_CHECKING:
    from src.models import RoomsOrm  # Импорт только для аннотаций (избегаем циклических импортов)


class FacilitiesOrm(Base):
    """
    ORM-модель таблицы 'facilities' — представляет удобства (услуги), доступные в комнатах.

    Примеры: Wi-Fi, кондиционер, завтрак включён.
    """

    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(primary_key=True)  # Уникальный идентификатор удобства
    title: Mapped[str] = mapped_column(String(100))  # Название удобства (макс. 100 символов)

    # Связь many-to-many с комнатами через промежуточную таблицу rooms_facilities
    rooms: Mapped[list["RoomsOrm"]] = relationship(
        back_populates="facilities",  # Обратная связь из модели RoomsOrm
        secondary="rooms_facilities",  # Название промежуточной таблицы
    )


class RoomsFacilitiesOrm(Base):
    """
    Промежуточная таблица 'rooms_facilities' для связи many-to-many между комнатами и удобствами.
    """

    __tablename__ = "rooms_facilities"

    id: Mapped[int] = mapped_column(primary_key=True)  # Уникальный ID связи
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))  # Внешний ключ на таблицу комнат
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))  # Внешний ключ на таблицу удобств
