from datetime import date
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from src.exceptions import RoomNotFoundException
from src.models.rooms import RoomsOrm  # ORM-модель комнат
from src.repositories.base import BaseRepository  # Базовый репозиторий
from src.repositories.mappers.mappers import (
    RoomDataMapper,
    RoomDataWithRelsMapper,
)  # Мапперы ORM → доменная модель
from src.repositories.utils import rooms_ids_for_booking  # Утилита для фильтрации доступных комнат по датам


class RoomsRepository(BaseRepository):
    """
    Репозиторий для работы с таблицей комнат.
    Содержит методы для получения комнат по фильтрам, включая связанные удобства.
    """

    model = RoomsOrm
    mapper = RoomDataMapper

    async def get_filtered_by_time(
        self,
        hotel_id: int,
        date_from: date,
        date_to: date,
    ):
        """
        Получение свободных комнат отеля в указанный диапазон дат.

        :param hotel_id: ID отеля
        :param date_from: дата начала периода бронирования
        :param date_to: дата окончания периода бронирования
        :return: список доменных сущностей комнат с удобствами
        """
        # Получаем ID всех свободных комнат для заданного отеля и дат
        rooms_ids_to_get = rooms_ids_for_booking(date_from, date_to, hotel_id)

        # Формируем запрос с жадной загрузкой удобств
        query = select(self.model).options(selectinload(self.model.facilities)).filter(RoomsOrm.id.in_(rooms_ids_to_get))

        result = await self.session.execute(query)

        # Преобразуем ORM-модели в доменные модели
        return [RoomDataWithRelsMapper.map_to_domain_entity(model) for model in result.unique().scalars().all()]

    async def get_one_with_rels(self, **filter_by):
        """
        Получение одной комнаты по фильтру с загрузкой удобств.

        :param filter_by: параметры фильтрации (например, id, hotel_id)
        :raises RoomNotFoundException: если комната не найдена
        :return: доменная модель комнаты с удобствами
        """
        # Жадно загружаем связанные удобства
        query = select(self.model).options(selectinload(self.model.facilities)).filter_by(**filter_by)
        result = await self.session.execute(query)

        try:
            model = result.scalar_one()
        except NoResultFound:
            raise RoomNotFoundException

        return RoomDataWithRelsMapper.map_to_domain_entity(model)
