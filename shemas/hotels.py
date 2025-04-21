from pydantic import BaseModel, Field   # импортируем класс BaseModel из pydantic


# Схема данных, которая описывает структуру входящих данных отеля.
class Hotel(BaseModel):
    title: str  # отображаемое название
    name: str   # внутреннее имя (например, slug)


# Схема данных, которая описывает структуру входящих данных отеля.
class HotelPatch(BaseModel):
    title: str | None = Field(None)
    name: str | None = Field(None)
