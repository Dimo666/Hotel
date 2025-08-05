from datetime import date

from fastapi import APIRouter, Body, Query
from src.api.dependencies import DBDep
from src.exceptions import check_dete_to_after_date_from, ObjectNotFoundException, RoomNotFoundException, HotelNotFoundException
from src.schemas.facilities import RoomFacilityAdd
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomPatchRequest, RoomPatch

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
    check_dete_to_after_date_from(date_from, date_to)
    return await db.rooms.get_filtered_by_time(
        hotel_id=hotel_id,
        date_from=date_from,
        date_to=date_to,
    )


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
    room = await db.rooms.get_one_or_none_with_rels(id=hotel_id)
    if not room:
        raise RoomNotFoundException


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
        await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundException

    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    room = await db.rooms.add(_room_data)

    rooms_facilities_data = [RoomFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in room_data.facilities_ids]
    await db.rooms_facilities.add_bulk(rooms_facilities_data)
    await db.commit()

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
    try:
        await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundException

    try:
        await db.rooms.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise RoomNotFoundException

    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    await db.rooms.edit(_room_data, id=room_id)
    await db.rooms_facilities.set_room_facilities(room_id, facilities_ids=room_data.facilities_ids)
    await db.commit()
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
    try:
        await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundException

    try:
        await db.rooms.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise RoomNotFoundException

    _room_data_dict = room_data.model_dump(exclude_unset=True)
    _room_data = RoomPatch(hotel_id=hotel_id, **_room_data_dict)

    await db.rooms.edit(_room_data, exclude_unset=True, id=room_id, hotel_id=hotel_id)

    if "facilities_ids" in _room_data_dict:
        await db.rooms_facilities.set_room_facilities(room_id, facilities_ids=_room_data_dict["facilities_ids"])

    await db.commit()
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
    try:
        await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundException

    try:
        await db.rooms.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise RoomNotFoundException

    await db.rooms.delete(id=room_id, hotel_id=hotel_id)
    await db.commit()
    return {"status": "OK"}
