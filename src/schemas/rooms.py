from pydantic import BaseModel, ConfigDict
from src.schemas.facilities import Facility  # Схема удобства (услуги)


class RoomAddRequest(BaseModel):
    """
    DTO-запрос от клиента для создания комнаты.
    Содержит ID удобств, но без привязки к отелю.

    Используется в POST /rooms.
    """
    title: str  # Название комнаты
    description: str | None = None  # Описание (необязательное)
    price: int  # Цена за ночь
    quantity: int  # Количество доступных экземпляров этой комнаты
    facilities_ids: list[int] = []  # Список ID удобств


class RoomAdd(BaseModel):
    """
    Внутренняя модель для создания комнаты в репозитории.
    Уже включает hotel_id, но без списка удобств.
    """
    hotel_id: int
    title: str
    description: str | None = None
    price: int
    quantity: int


class Room(RoomAdd):
    """
    Схема ответа клиенту с ID созданной комнаты.

    Наследует все поля из RoomAdd и добавляет `id`.
    """
    id: int

    model_config = ConfigDict(from_attributes=True)  # Позволяет создавать из ORM


class RoomWithRels(Room):
    """
    Комната с подгруженными удобствами (many-to-many).

    Используется в ответах, где нужно показать связанные удобства.
    """
    facilities: list[Facility]


class RoomPatchRequest(BaseModel):
    """
    DTO-запрос от клиента на частичное обновление комнаты (PATCH).

    Все поля являются необязательными.
    """
    title: str | None = None
    description: str | None = None
    price: int | None = None
    quantity: int | None = None
    facilities_ids: list[int] = []  # Обновляемый список удобств


class RoomPatch(BaseModel):
    """
    Модель, передаваемая в репозиторий для частичного обновления комнаты.

    Обычно собирается из RoomPatchRequest + hotel_id.
    """
    hotel_id: int | None = None
    title: str | None = None
    description: str | None = None
    price: int | None = None
    quantity: int | None = None
