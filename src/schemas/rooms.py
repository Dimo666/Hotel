from pydantic import BaseModel, Field, ConfigDict  # импортируем класс BaseModel из pydantic



class RoomAdd(BaseModel):
    title: str  # отображаемое название
    description: str | None
    price: int
    quantity: int

class Room(RoomAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RoomCreate(RoomAdd):
    hotel_id: int



class RoomPatch(BaseModel):
    title: str | None = Field(None)# отображаемое название
    description: str | None = Field(None)
    price: int | None = Field(None)
    quantity: int | None = Field(None)