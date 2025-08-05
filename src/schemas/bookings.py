from datetime import date

from pydantic import BaseModel, ConfigDict


# Запрос от клиента на бронирование комнаты (без user_id и цены)
class BookingAddRequest(BaseModel):
    room_id: int
    date_from: date
    date_to: date


# Модель для создания бронирования на уровне бизнес-логики / БД
class BookingAdd(BaseModel):
    user_id: int
    room_id: int
    date_from: date
    date_to: date
    price: int  # Итоговая цена бронирования (обычно рассчитывается на бэке)


# Ответ клиенту: полные данные о бронировании, включая ID
class Booking(BookingAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)  # Позволяет создавать из ORM-объекта

