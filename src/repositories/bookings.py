from datetime import date
from fastapi import HTTPException


from sqlalchemy import select

from src.exceptions import AllRoomsAreBookedException
from src.models.bookings import BookingsOrm  # ORM-модель бронирования
from src.repositories.base import BaseRepository  # Базовый репозиторий с session
from src.repositories.mappers.mappers import BookingDataMapper  # Маппер ORM → Domain Entity
from src.repositories.utils import rooms_ids_for_booking
from src.schemas.bookings import BookingAdd


class BookingsRepository(BaseRepository):
    model = BookingsOrm  # Указываем модель для базовых операций
    mapper = BookingDataMapper  # Указываем маппер для преобразования данных

    # Получить бронирования, у которых заезд сегодня
    async def get_bookings_with_today_checkin(self):
        query = select(BookingsOrm).filter(BookingsOrm.date_from == date.today())  # Сравнение даты заезда с сегодняшней датой
        res = await self.session.execute(query)  # Выполнение запроса
        return [self.mapper.map_to_domain_entity(booking) for booking in res.scalars().all()]  # Преобразование ORM-объектов в доменные сущности через маппер

    async def add_booking(self, data: BookingAdd, hotel_id: int):  # Получаем SQL-запрос на свободные комнаты в указанный период и отеле
        rooms_ids_to_get = rooms_ids_for_booking(
            date_from=data.date_from,
            date_to=data.date_to,
            hotel_id=hotel_id,
        )
        rooms_ids_to_book_res = await self.session.execute(rooms_ids_to_get)  # Выполняем запрос к базе данных
        rooms_ids_to_book: list[int] = rooms_ids_to_book_res.scalars().all()  # Извлекаем список ID доступных комнат

        if data.room_id in rooms_ids_to_book:  # Проверяем, входит ли нужная комната в список доступных
            # Если да — создаём бронь и возвращаем её
            new_booking = await self.add(data)
            return new_booking
        raise AllRoomsAreBookedException
