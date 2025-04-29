from fastapi import APIRouter, Body

from src.database import async_session_maker
from src.repositories.rooms import RoomsRepository
from src.schemas.rooms import RoomAdd, RoomCreate, RoomPatch

router = APIRouter(prefix="/hotel", tags=["Номера"])


@router.get("/rooms")
async def get_rooms(

):
    async with async_session_maker() as session:
        return await RoomsRepository(session).get_all()


@router.get("/rooms/{room_id}")
async def get_room(
    room_id: int,
):
    async with async_session_maker() as session:
        return await RoomsRepository(session).get_one_or_none(
            id=room_id,
        )


@router.post("/{hotel_id}/rooms")
async def create_rooms(
        hotel_id: int,
        rooms: RoomAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Luxury",
                "value": {
                    "title": "Luxury",
                    "description": "*****",
                    "price": "200",
                    "quantity": "1",
                },
            },
            "2": {
                "summary": "Start",
                "value": {
                    "title": "Start room",
                    "description": "***",
                    "price": "50",
                    "quantity": "1",
                },
            },
        }
    )
):
    async with async_session_maker() as session:
        # Объединяем данные для вставки
        room_data = rooms.model_dump()
        room_data['hotel_id'] = hotel_id

        # Передаём уже правильную схему
        room_create = RoomCreate(**room_data)
        new_room = await RoomsRepository(session).add(room_create)
        await session.commit()
    return {"status": "OK", "data": new_room}


@router.put("/rooms/{room_id}")
async def edit_rooms(
        room_id: int,
        room_data: RoomAdd,
):
    async with async_session_maker() as session:
        await RoomsRepository(session).edit(room_data, id=room_id)
        await session.commit()
    return {"status": "OK", "data": room_data}


@router.patch("/rooms/{room_id}")
async def partially_edit_rooms(
        room_id: int,
        room_data: RoomPatch,
):
    async with async_session_maker() as session:
        await RoomsRepository(session).edit(room_data, exclude_unset=True, id=room_id)
        await session.commit()
    return {"status": "OK"}


@router.delete("/rooms/{room_id}")
async def delete_rooms(room_id: int):
    async with async_session_maker() as session:
        await RoomsRepository(session).delete(id=room_id)
        await session.commit()
    return {"status": "OK"}