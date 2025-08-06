from pydantic import BaseModel, Field, ConfigDict


class HotelAdd(BaseModel):
    """
    Схема для создания нового отеля (используется в POST /hotels).

    Пример:
    {
        "title": "Hilton",
        "location": "new-york"
    }
    """
    title: str  # Название отеля
    location: str  # Локация или slug (например, "paris", "berlin")


class Hotel(HotelAdd):
    """
    Схема для возврата отеля клиенту. Включает ID отеля.

    Наследует поля из HotelAdd и добавляет `id`.
    """
    id: int

    model_config = ConfigDict(from_attributes=True)  # Позволяет создавать модель из ORM-объекта


class HotelPatch(BaseModel):
    """
    Схема для частичного обновления отеля (используется в PATCH /hotels/{id}).

    Все поля являются необязательными.
    """
    title: str | None = Field(default=None)     # Новое название отеля
    location: str | None = Field(default=None)  # Новая локация (slug)
