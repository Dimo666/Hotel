from pydantic import BaseModel, Field, ConfigDict


# Схема для создания отеля (POST /hotels)
class HotelAdd(BaseModel):
    title: str  # Название отеля
    location: str  # Локация или slug


# Схема для возврата отеля с ID (в ответах клиенту)
class Hotel(HotelAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)  # Поддержка создания из ORM-модели


# Схема для обновления отеля (PATCH /hotels/{id})
class HotelPatch(BaseModel):
    title: str | None = Field(default=None)  # Обновляемое название
    location: str | None = Field(default=None)  # Обновляемая локация
