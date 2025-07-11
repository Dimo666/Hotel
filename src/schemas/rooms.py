from pydantic import BaseModel, ConfigDict
from src.schemas.facilities import Facility  # Pydantic-модель удобства


# DTO-запрос для создания комнаты от клиента (с ID удобств)
class RoomAddRequest(BaseModel):
    title: str
    description: str | None = None
    price: int
    quantity: int
    facilities_ids: list[int] = []  # Список ID удобств


# Модель, отправляемая в репозиторий для создания комнаты (без удобств)
class RoomAdd(BaseModel):
    hotel_id: int
    title: str
    description: str | None = None
    price: int
    quantity: int


# Ответ клиенту: созданная комната с ID
class Room(RoomAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)  # Позволяет создавать из ORM-модели через `from_orm()` или `from_attributes()`


# Комната с подгруженными удобствами (используется в ответах)
class RoomWithRels(Room):
    facilities: list[Facility]


# DTO-запрос для PATCH (обновление комнаты)
class RoomPatchRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = None
    quantity: int | None = None
    facilities_ids: list[int] = []


# Модель для передачи в репозиторий при обновлении
class RoomPatch(BaseModel):
    hotel_id: int | None = None
    title: str | None = None
    description: str | None = None
    price: int | None = None
    quantity: int | None = None
