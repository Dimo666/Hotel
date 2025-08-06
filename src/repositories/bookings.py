from datetime import date
from fastapi import HTTPException
from sqlalchemy import select

from src.exceptions import AllRoomsAreBookedException
from src.models.bookings import BookingsOrm  # ORM-модель бронирований
from src.repositories.base import BaseRepository  # Базовый репозиторий
from src.repositories.mappers.mappers import BookingDataMapper  # Маппер ORM → доменная модель
from src.repositories.utils import rooms_ids_for_booking  # Функция получения ID доступных комнат
from src.schemas.bookings import BookingAdd  # Pydantic-схема для создания брони


class BookingsRepository(BaseRepository):
    """
    Репозиторий для работы с бронированиями.
    Позволяет добавлять брони и получать список броней с заездом на сегодня.
    """

    model = BookingsOrm
    mapper = BookingDataMapper

    async def get_bookings_with_today_checkin(self):
        """
        Получение всех бронирований, у которых дата заезда — сегодня.

        :return: список доменных сущностей бронирований
        """
        query = select(BookingsOrm).filter(BookingsOrm.date_from == date.today())

        res = await self.session.execute(query)

        return [
            self.mapper.map_to_domain_entity(booking)
            for booking in res.scalars().all()
        ]

    async def add_booking(self, data: BookingAdd, hotel_id: int):
        """
        Добавление нового бронирования, если комната действительно доступна в указанные даты.

        :param data: данные для бронирования (room_id, date_from, date_to, user_id)
        :param hotel_id: ID отеля, в котором запрашивается комната
        :raises AllRoomsAreBookedException: если указанная комната недоступна
        :return: объект созданной брони
        """
        # Получаем SQL-запрос на доступные комнаты
        rooms_ids_to_get = rooms_ids_for_booking(
            date_from=data.date_from,
            date_to=data.date_to,
            hotel_id=hotel_id,
        )

        # Выполняем запрос и получаем список ID доступных комнат
        rooms_ids_to_book_res = await self.session.execute(rooms_ids_to_get)
        rooms_ids_to_book: list[int] = rooms_ids_to_book_res.scalars().all()

        # Если нужная комната доступна — создаём бронь
        if data.room_id in rooms_ids_to_book:
            new_booking = await self.add(data)
            return new_booking

        # Иначе — выбрасываем исключение
        raise AllRoomsAreBookedException
