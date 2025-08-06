from datetime import date

from src.exceptions import check_date_to_after_date_from, ObjectNotFoundException, HotelNotFoundException
from src.schemas.hotels import HotelAdd, HotelPatch, Hotel
from src.services.base import BaseService


class HotelService(BaseService):
    """
    Сервис для управления отелями: фильтрация, создание, обновление, удаление.
    """

    async def get_hotels(
        self,
        pagination,               # Параметры пагинации: страница и количество элементов на страницу
        location: str | None,     # Локация отеля (опционально)
        title: str | None,        # Название отеля (опционально)
        date_from: date,          # Дата начала периода
        date_to: date             # Дата конца периода
    ):
        """
        Получение списка отелей по фильтрам: локация, название, дата, пагинация.

        - Проверяет корректность диапазона дат
        - Проводит фильтрацию на уровне базы данных

        :param pagination: объект с полями `page` и `per_page`
        :param location: фильтрация по локации (необязательно)
        :param title: фильтрация по названию (необязательно)
        :param date_from: дата начала периода
        :param date_to: дата конца периода
        :return: список подходящих отелей
        """
        check_date_to_after_date_from(date_from, date_to)  # Проверка корректности дат

        per_page = pagination.per_page or 5  # Значение по умолчанию
        offset = per_page * (pagination.page - 1)

        # Получение отелей с фильтрацией и пагинацией
        return await self.db.hotels.get_filtered_by_time(
            date_from=date_from,
            date_to=date_to,
            location=location,
            title=title,
            limit=per_page,
            offset=offset,
        )

    async def get_hotel(self, hotel_id: int):
        """
        Получение одного отеля по ID.

        :param hotel_id: идентификатор отеля
        :return: объект отеля
        """
        return await self.db.hotels.get_one(id=hotel_id)

    async def add_hotel(self, data: HotelAdd):
        """
        Создание нового отеля.

        :param data: входные данные отеля
        :return: созданный отель
        """
        hotel = await self.db.hotels.add(data)
        await self.db.commit()
        return hotel

    async def edit_hotel(self, hotel_id: int, data: HotelAdd):
        """
        Полное обновление информации об отеле (PUT).

        :param hotel_id: ID отеля
        :param data: новые данные (все поля обязательны)
        :return: None
        """
        await self.db.hotels.edit(data, id=hotel_id)
        await self.db.commit()

    async def edit_hotel_partially(self, hotel_id: int, data: HotelPatch, exclude_unset: bool = False):
        """
        Частичное обновление информации об отеле (PATCH).

        :param hotel_id: ID отеля
        :param data: изменяемые поля (не все поля обязательны)
        :param exclude_unset: флаг для обновления только переданных полей
        :return: None
        """
        await self.db.hotels.edit(data, exclude_unset=exclude_unset, id=hotel_id)
        await self.db.commit()

    async def delete_hotel(self, hotel_id: int):
        """
        Удаление отеля по ID.

        :param hotel_id: ID удаляемого отеля
        :return: None
        """
        await self.db.hotels.delete(id=hotel_id)
        await self.db.commit()

    async def get_hotel_with_check(self, hotel_id: int) -> Hotel:
        """
        Получение отеля с проверкой существования.

        :param hotel_id: ID отеля
        :raises HotelNotFoundException: если отель не найден
        :return: объект Hotel
        """
        try:
            return await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException:
            raise HotelNotFoundException
