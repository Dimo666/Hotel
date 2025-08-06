# Импорт ORM-моделей для централизованного экспорта

from src.models.hotels import HotelsOrm        # Модель отеля
from src.models.rooms import RoomsOrm          # Модель комнаты
from src.models.users import UsersOrm          # Модель пользователя
from src.models.bookings import BookingsOrm    # Модель бронирования
from src.models.facilities import FacilitiesOrm  # Модель удобства (услуги)

# Указываем, какие модели экспортируются при использовании `from src.models import *`
__all__ = [
    "HotelsOrm",
    "RoomsOrm",
    "UsersOrm",
    "BookingsOrm",
    "FacilitiesOrm",
]
