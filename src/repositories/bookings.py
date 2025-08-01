from datetime import date
from sqlalchemy import select

from src.models import RoomsOrm
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
        query = (
            select(BookingsOrm)
            .filter(BookingsOrm.date_from == date.today())  # Сравнение даты заезда с сегодняшней датой
        )
        res = await self.session.execute(query)  # Выполнение запроса
        # Преобразование ORM-объектов в доменные сущности через маппер
        return [self.mapper.map_to_domain_entity(booking) for booking in res.scalars().all()]

    async def add_booking(self, booking_data: BookingAdd):
        # Получаем комнату (для hotel_id и проверки на существование)
        room = await self.session.get(RoomsOrm, booking_data.room_id)
        if not room:
            raise Exception("Комната не найдена")

        # Получаем SELECT-запрос со списком доступных комнат
        stmt = rooms_ids_for_booking(
            date_from=booking_data.date_from,
            date_to=booking_data.date_to,
            hotel_id=room.hotel_id
        )

        # Выполняем запрос и получаем список доступных ID
        result = await self.session.execute(stmt)
        available_room_ids = [row[0] for row in result.all()]

        # Проверяем, доступна ли нужная комната
        if booking_data.room_id not in available_room_ids:
            raise Exception("Нет свободных номеров")

        # Всё ок — создаём бронь
        orm_booking = self.mapper.map_to_persistence_entity(booking_data)
        self.session.add(orm_booking)
        await self.session.flush()

        return self.mapper.map_to_domain_entity(orm_booking)
