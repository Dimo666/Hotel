from src.models.hotels import HotelsOrm  # Модель отеля
from src.models.rooms import RoomsOrm  # Модель номера
from src.models.users import UsersOrm  # Модель пользователя
from src.models.bookings import BookingsOrm  # Модель бронирования
from src.models.facilities import FacilitiesOrm

__all__ = [
    "HotelsOrm",
    "RoomsOrm",
    "UsersOrm",
    "BookingsOrm",
    "FacilitiesOrm",
]
