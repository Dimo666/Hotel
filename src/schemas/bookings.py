from datetime import date
from pydantic import BaseModel, ConfigDict


class BookingAddRequest(BaseModel):
    """
    Схема запроса от клиента для бронирования комнаты.

    Используется в ручке POST /bookings.
    Клиент передаёт ID комнаты и даты заезда/выезда.
    """
    room_id: int
    date_from: date
    date_to: date


class BookingAdd(BaseModel):
    """
    Схема для внутренней бизнес-логики:
    используется для создания записи в базе.

    Добавляется user_id и вычисленная цена.
    """
    user_id: int
    room_id: int
    date_from: date
    date_to: date
    price: int  # Итоговая цена бронирования, рассчитывается на бэке


class Booking(BookingAdd):
    """
    Схема ответа клиенту: полные данные о бронировании.

    Наследует все поля из BookingAdd + добавляет id.
    """
    id: int

    model_config = ConfigDict(from_attributes=True)  # Автоматическое преобразование из ORM
