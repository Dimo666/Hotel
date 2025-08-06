from datetime import date
from sqlalchemy import select, func

from src.models.hotels import HotelsOrm  # ORM-модель отелей
from src.models.rooms import RoomsOrm    # ORM-модель комнат
from src.repositories.base import BaseRepository  # Базовый репозиторий
from src.repositories.mappers.mappers import HotelDataMapper  # Маппер ORM → доменная модель
from src.repositories.utils import rooms_ids_for_booking  # Утилита для фильтрации свободных комнат


class HotelsRepository(BaseRepository):
    """
    Репозиторий для работы с отелями. Содержит методы фильтрации по доступности и другим параметрам.
    """

    model = HotelsOrm
    mapper = HotelDataMapper

    async def get_filtered_by_time(
        self,
        date_from: date,
        date_to: date,
        location: str | None = None,
        title: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ):
        """
        Получение отелей, у которых есть хотя бы одна свободная комната в заданном диапазоне дат.
        Также поддерживается фильтрация по локации и названию.

        :param date_from: дата заезда
        :param date_to: дата выезда
        :param location: фильтрация по локации (необязательно)
        :param title: фильтрация по названию (необязательно)
        :param limit: количество отелей на странице
        :param offset: смещение для пагинации
        :return: список доменных сущностей отелей
        """
        # Получаем список ID свободных комнат за указанный период
        rooms_ids_to_get = rooms_ids_for_booking(date_from=date_from, date_to=date_to)

        # Получаем ID отелей, в которых есть такие свободные комнаты
        hotels_ids_to_get = (
            select(RoomsOrm.hotel_id)
            .select_from(RoomsOrm)
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        )

        # Формируем запрос к таблице отелей с фильтрацией по наличию свободных комнат
        query = select(HotelsOrm).filter(HotelsOrm.id.in_(hotels_ids_to_get))

        # Фильтрация по локации (регистронезависимо)
        if location:
            query = query.filter(
                func.lower(HotelsOrm.location).contains(location.strip().lower())
            )

        # Фильтрация по названию (регистронезависимо)
        if title:
            query = query.filter(
                func.lower(HotelsOrm.title).contains(title.strip().lower())
            )

        # Применяем пагинацию
        query = query.limit(limit).offset(offset)

        # Выполняем запрос и маппим результат в доменные модели
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(hotel) for hotel in result.scalars().all()]
