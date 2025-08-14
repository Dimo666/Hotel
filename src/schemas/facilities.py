from pydantic import BaseModel, ConfigDict


class FacilityAdd(BaseModel):
    """
    Схема для добавления нового удобства (услуги) через API.

    Пример: {"title": "Wi-Fi"}
    """

    title: str


class Facility(FacilityAdd):
    """
    Схема ответа с удобством, включает ID.

    Используется при возврате данных клиенту.
    """

    id: int

    model_config = ConfigDict(from_attributes=True)  # Позволяет создавать модель из ORM-объекта


class RoomFacilityAdd(BaseModel):
    """
    Схема для создания связи между комнатой и удобством (many-to-many).

    Пример: {"room_id": 1, "facility_id": 3}
    """

    room_id: int
    facility_id: int


class RoomFacility(RoomFacilityAdd):
    """
    Схема для ответа с ID связи между комнатой и удобством.

    Используется при возврате данных из базы.
    """

    id: int
