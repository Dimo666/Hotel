from datetime import date
from sqlalchemy import select

from src.models.bookings import BookingsOrm  # ORM-модель бронирования
from src.repositories.base import BaseRepository  # Базовый репозиторий с session
from src.repositories.mappers.mappers import BookingDataMapper  # Маппер ORM → Domain Entity


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
