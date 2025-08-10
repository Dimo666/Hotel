from datetime import date

from src.exceptions import check_date_to_after_date_from, ObjectNotFoundException, HotelNotFoundException, \
    RoomNotFoundException
from src.schemas.facilities import RoomFacilityAdd
from src.schemas.rooms import RoomAddRequest, Room, RoomAdd, RoomPatchRequest, RoomPatch
from src.services.base import BaseService
from src.services.hotels import HotelService


class RoomService(BaseService):
    """
    Сервис для управления комнатами в отеле:
    создание, обновление, удаление и получение информации о комнатах.
    """

    async def get_filtered_by_time(self, hotel_id: int, date_from: date, date_to: date):
        """
        Получение списка свободных комнат в отеле по диапазону дат.

        :param hotel_id: ID отеля
        :param date_from: дата заезда
        :param date_to: дата выезда
        :return: список комнат
        """
        check_date_to_after_date_from(date_from, date_to)  # Проверка валидности дат
        return await self.db.rooms.get_filtered_by_time(
            hotel_id=hotel_id,
            date_from=date_from,
            date_to=date_to
        )

    async def get_room(self, room_id: int, hotel_id: int):
        """
        Получение информации о комнате вместе с удобствами.

        :param hotel_id: ID отеля
        :param room_id: ID комнаты
        :raises RoomNotFoundException: если комната не найдена
        :return: объект комнаты
        """
        return await self.db.rooms.get_one_with_rels(id=room_id, hotel_id=hotel_id)

    async def create_room(self, hotel_id: int, room_data: RoomAddRequest):
        """
        Создание новой комнаты и привязка удобств.

        :param hotel_id: ID отеля
        :param room_data: данные о комнате и список ID удобств
        :raises HotelNotFoundException: если отель не найден
        :return: None
        """
        # Проверяем, существует ли отель
        try:
            await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException as ex:
            raise HotelNotFoundException from ex

        # Создаём объект комнаты
        _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        room: Room = await self.db.rooms.add(_room_data)

        # Создаём связи с удобствами
        rooms_facilities_data = [
            RoomFacilityAdd(room_id=room.id, facility_id=f_id)
            for f_id in room_data.facilities_ids
        ]
        # если нет удобств тогда не исполняем код
        if rooms_facilities_data:
            await self.db.rooms_facilities.add_bulk(rooms_facilities_data)

        await self.db.commit()

    async def edit_room(self, hotel_id: int, room_id: int, room_data: RoomAddRequest):
        """
        Полное обновление данных комнаты.

        :param hotel_id: ID отеля
        :param room_id: ID комнаты
        :param room_data: новые данные о комнате
        :raises HotelNotFoundException: если отель не найден
        :raises RoomNotFoundException: если комната не найдена
        :return: None
        """
        await HotelService(self.db).get_hotel_with_check(hotel_id)  # Проверка отеля
        await self.get_room_with_check(room_id)  # Проверка комнаты

        # Создаём обновлённый объект
        _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        await self.db.rooms.edit(_room_data, id=room_id)

        # Обновляем удобства
        await self.db.rooms_facilities.set_room_facilities(
            room_id, facilities_ids=room_data.facilities_ids
        )
        await self.db.commit()

    async def partially_edit_room(self, hotel_id: int, room_id: int, room_data: RoomPatchRequest):
        """
        Частичное обновление данных комнаты.

        :param hotel_id: ID отеля
        :param room_id: ID комнаты
        :param room_data: изменяемые поля и удобства
        :raises HotelNotFoundException: если отель не найден
        :raises RoomNotFoundException: если комната не найдена
        :return: None
        """
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.get_room_with_check(room_id)

        # Получаем только переданные поля (exclude_unset)
        _room_data_dict = room_data.model_dump(exclude_unset=True)

        # Обновляем только указанные поля
        _room_data = RoomPatch(hotel_id=hotel_id, **_room_data_dict)
        await self.db.rooms.edit(
            _room_data,
            exclude_unset=True,
            id=room_id,
            hotel_id=hotel_id
        )

        # Если переданы новые удобства — обновляем связи
        if "facilities_ids" in _room_data_dict:
            await self.db.rooms_facilities.set_room_facilities(
                room_id, facilities_ids=_room_data_dict["facilities_ids"]
            )

        await self.db.commit()

    async def delete_room(self, hotel_id: int, room_id: int):
        """
        Удаление комнаты из отеля.

        :param hotel_id: ID отеля
        :param room_id: ID комнаты
        :raises HotelNotFoundException: если отель не найден
        :raises RoomNotFoundException: если комната не найдена
        :return: None
        """
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.get_room_with_check(room_id)

        await self.db.rooms.delete(id=room_id, hotel_id=hotel_id)
        await self.db.commit()

    async def get_room_with_check(self, room_id: int) -> Room:
        """
        Получение комнаты с проверкой на существование.

        :param room_id: ID комнаты
        :raises RoomNotFoundException: если комната не найдена
        :return: объект Room
        """
        try:
            return await self.db.rooms.get_one(id=room_id)
        except ObjectNotFoundException:
            raise RoomNotFoundException
