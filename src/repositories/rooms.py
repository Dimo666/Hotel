from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.exceptions import InvalidDateRangeException
from src.models.rooms import RoomsOrm  # ORM-модель комнат
from src.repositories.base import BaseRepository  # Базовый репозиторий
from src.repositories.mappers.mappers import (
    RoomDataMapper,
    RoomDataWithRelsMapper,
)  # Мапперы ORM → доменная модель
from src.repositories.utils import (
    rooms_ids_for_booking,
)  # Утилита для фильтрации доступных комнат по датам


class RoomsRepository(BaseRepository):
    model = RoomsOrm  # Основная модель
    mapper = RoomDataMapper  # Базовый маппер

    # Получение комнат по отелю и диапазону дат (только свободные)
    async def get_filtered_by_time(
        self,
        hotel_id,
        date_from: date,
        date_to: date,
    ):

        # Проверка диапазона дат
        if date_from > date_to:
            raise InvalidDateRangeException()

        # Получаем список ID свободных комнат
        rooms_ids_to_get = rooms_ids_for_booking(date_from, date_to, hotel_id)

        # Загружаем комнаты и связанные удобства (facilities) одним запросом
        query = select(self.model).options(selectinload(self.model.facilities)).filter(RoomsOrm.id.in_(rooms_ids_to_get))

        result = await self.session.execute(query)

        # Преобразуем ORM-модели в доменные сущности
        return [RoomDataWithRelsMapper.map_to_domain_entity(model) for model in result.unique().scalars().all()]

    # Получение одной комнаты с удобствами по фильтру
    async def get_one_or_none_with_rels(self, **filter_by):
        query = (
            select(self.model)
            .options(selectinload(self.model.facilities))  # Жадная загрузка удобств
            .filter_by(**filter_by)  # Универсальный фильтр по параметрам
        )
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()

        if model is None:
            return None

        return RoomDataWithRelsMapper.map_to_domain_entity(model)
