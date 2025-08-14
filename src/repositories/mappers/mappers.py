from src.models.bookings import BookingsOrm
from src.models.facilities import FacilitiesOrm
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.models.users import UsersOrm

from src.repositories.mappers.base import DataMapper  # Базовый маппер ORM → схема
from src.schemas.bookings import Booking
from src.schemas.facilities import Facility
from src.schemas.hotels import Hotel
from src.schemas.rooms import Room, RoomWithRels
from src.schemas.users import User


class HotelDataMapper(DataMapper):
    """
    Маппер данных отеля:
    ORM-модель → Pydantic-схема Hotel
    """

    db_model = HotelsOrm
    schema = Hotel


class RoomDataMapper(DataMapper):
    """
    Маппер для комнаты:
    ORM-модель → Pydantic-схема Room (без связей)
    """

    db_model = RoomsOrm
    schema = Room


class RoomDataWithRelsMapper(DataMapper):
    """
    Маппер для комнаты с отношениями (удобства и др. связи):
    ORM-модель → Pydantic-схема RoomWithRels
    """

    db_model = RoomsOrm
    schema = RoomWithRels


class UserDataMapper(DataMapper):
    """
    Маппер пользователя:
    ORM-модель → Pydantic-схема User
    """

    db_model = UsersOrm
    schema = User


class BookingDataMapper(DataMapper):
    """
    Маппер бронирования:
    ORM-модель → Pydantic-схема Booking
    """

    db_model = BookingsOrm
    schema = Booking


class FacilityDataMapper(DataMapper):
    """
    Маппер услуги (удобства):
    ORM-модель → Pydantic-схема Facility
    """

    db_model = FacilitiesOrm
    schema = Facility
