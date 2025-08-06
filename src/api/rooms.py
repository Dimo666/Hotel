from datetime import date

from fastapi import APIRouter, Body, Query
from src.api.dependencies import DBDep
from src.exceptions import RoomNotFoundException, HotelNotFoundException, \
    HotelNotFoundHTTPException, RoomNotFoundHTTPException
from src.schemas.rooms import RoomAddRequest, RoomPatchRequest
from src.services.rooms import RoomService

# Создаём роутер с префиксом /hotels и тегом "Номера"
router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms")
async def get_rooms(
    hotel_id: int,
    db: DBDep,
    date_from: date = Query(example="2024-08-01"),
    date_to: date = Query(example="2024-08-10"),
):
    """
    Получение списка свободных комнат в отеле по диапазону дат.

    :param hotel_id: ID отеля
    :param db: доступ к БД
    :param date_from: дата заезда
    :param date_to: дата выезда
    :return: список комнат
    """
    return await RoomService(db).get_filtered_by_time(hotel_id, date_from, date_to)


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(hotel_id: int, room_id: int, db: DBDep):
    """
    Получение информации о комнате вместе с удобствами.

    :param hotel_id: ID отеля
    :param room_id: ID комнаты
    :param db: доступ к БД
    :raises RoomNotFoundException: если комната не найдена
    :return: объект комнаты
    """
    try:
        return await db.rooms.get_one_or_none_with_rels(id=room_id, hotel_id=hotel_id)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException


@router.post("/{hotel_id}/rooms")
async def create_room(hotel_id: int, db: DBDep, room_data: RoomAddRequest = Body()):
    """
    Создание новой комнаты и связей с удобствами.

    :param hotel_id: ID отеля
    :param db: доступ к БД
    :param room_data: данные о комнате и список ID удобств
    :raises HotelNotFoundException: если отель не найден
    :return: статус и созданная комната
    """
    try:
        room = await RoomService(db).create_room(hotel_id, room_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException

    return {"status": "OK", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def edit_room(hotel_id: int, room_id: int, room_data: RoomAddRequest, db: DBDep):
    """
    Полное обновление данных комнаты.

    :param hotel_id: ID отеля
    :param room_id: ID комнаты
    :param room_data: новые данные
    :raises HotelNotFoundException: если отель не найден
    :raises RoomNotFoundException: если комната не найдена
    :return: статус
    """
    await RoomService(db).edit_room(hotel_id, room_id, room_data)
    return {"status": "OK"}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def partially_edit_room(hotel_id: int, room_id: int, room_data: RoomPatchRequest, db: DBDep):
    """
    Частичное обновление данных комнаты.

    :param hotel_id: ID отеля
    :param room_id: ID комнаты
    :param room_data: изменяемые поля и удобства
    :raises HotelNotFoundException: если отель не найден
    :raises RoomNotFoundException: если комната не найдена
    :return: статус
    """
    await RoomService(db).partially_edit_room(hotel_id, room_id, room_data)

    return {"status": "OK"}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(hotel_id: int, room_id: int, db: DBDep):
    """
    Удаление комнаты из отеля.

    :param hotel_id: ID отеля
    :param room_id: ID комнаты
    :raises HotelNotFoundException: если отель не найден
    :raises RoomNotFoundException: если комната не найдена
    :return: статус
    """
    await RoomService(db).delete_room(hotel_id, room_id)
    return {"status": "OK"}
