from pydantic import BaseModel, ConfigDict


# Схема для добавления нового удобства
class FacilityAdd(BaseModel):
    title: str


# Схема для возврата удобства с ID (используется в ответах)
class Facility(FacilityAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)  # Позволяет создавать модель из ORM-объекта


# Схема для связи комнаты и удобства (многие-ко-многим)
class RoomFacilityAdd(BaseModel):
    room_id: int
    facility_id: int


# Схема для возврата связи комнаты и удобства с ID
class RoomFacility(RoomFacilityAdd):
    id: int
