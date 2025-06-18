from datetime import date

from fastapi import APIRouter, Body, Query
from src.api.dependencies import DBDep
from src.schemas.facilities import RoomFacilityAdd
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomPatchRequest, RoomPatch

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms")
async def get_rooms(
        hotel_id: int,
        db: DBDep,
        date_from: date = Query(example="2024-08-01"),
        date_to: date = Query(example="2024-08-10"),
):
    return await db.rooms.get_filtered_by_time(hotel_id=hotel_id, date_from=date_from, date_to=date_to)


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(
        hotel_id: int,
        room_id: int,
        db: DBDep
):

    return await db.rooms.get_one_or_none(id=room_id, hotel_id=hotel_id)


@router.post("/{hotel_id}/rooms")
async def create_room(
        hotel_id: int,
        db: DBDep,
        room_data: RoomAddRequest = Body()
):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    room = await db.rooms.add(_room_data)

    rooms_facilities_data = [RoomFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in room_data.facilities_ids]
    await db.rooms_facilities.add_bulk(rooms_facilities_data)
    await db.commit()

    return {"status": "OK", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def edit_room(
        hotel_id: int,
        room_id: int,
        room_data: RoomAddRequest,
        db: DBDep
):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    await db.rooms.edit(_room_data, id=room_id)

    if room_data.facilities_ids is not None:
        existing_ids = await db.rooms_facilities.get_facility_ids_by_room(room_id)
        new_ids = set(room_data.facilities_ids)

        to_add = new_ids - existing_ids
        to_remove = existing_ids - new_ids

        if to_remove:
            await db.rooms_facilities.delete_by_room_and_facility_ids(room_id, list(to_remove))

        if to_add:
            facilities_to_add = [
                RoomFacilityAdd(room_id=room_id, facility_id=f_id)
                for f_id in to_add
            ]
            await db.rooms_facilities.add_bulk(facilities_to_add)

    await db.commit()
    return {"status": "OK", "data": room_data}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def partially_edit_room(
        hotel_id: int,
        room_id: int,
        room_data: RoomPatchRequest,
        db: DBDep
):
    _room_data = RoomPatch(hotel_id=hotel_id, **room_data.model_dump(exclude_unset=True))
    await db.rooms.edit(_room_data, exclude_unset=True, id=room_id, hotel_id=hotel_id)

    if room_data.facilities_ids is not None:
        existing_ids = await db.rooms_facilities.get_facility_ids_by_room(room_id)
        new_ids = set(room_data.facilities_ids)

        to_add = new_ids - existing_ids
        to_remove = existing_ids - new_ids

        if to_remove:
            await db.rooms_facilities.delete_by_room_and_facility_ids(room_id, list(to_remove))

        if to_add:
            facilities_to_add = [
                RoomFacilityAdd(room_id=room_id, facility_id=f_id)
                for f_id in to_add
            ]
            await db.rooms_facilities.add_bulk(facilities_to_add)

    await db.commit()
    return {"status": "OK", "data": room_data}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(
        hotel_id: int,
        room_id: int,
        db: DBDep
):
    await db.rooms.delete(id=room_id, hotel_id=hotel_id)
    await db.commit()
    return {"status": "OK"}