from pydantic import BaseModel, Field, ConfigDict  # импортируем класс BaseModel из pydantic


# Схема данных, которая описывает структуру входящих данных отеля.
class HotelAdd(BaseModel):
    title: str  # отображаемое название
    location: str   # внутреннее имя (например, slug)


class Hotel(HotelAdd):
    id: int


# Схема данных, которая описывает структуру входящих данных отеля.
class HotelPatch(BaseModel):
    title: str | None = Field(None)
    location: str | None = Field(None)
