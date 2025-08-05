from datetime import date
from fastapi_cache.decorator import cache
from fastapi import APIRouter, Body, Query, HTTPException

from src.api.dependencies import PaginationDep, DBDep
from src.exceptions import InvalidDateRangeException, NoHotelsFoundException
from src.schemas.hotels import HotelPatch, HotelAdd

# Роутер для работы с отелями
router = APIRouter(prefix="/hotels", tags=["Отели"])


# Получение списка отелей с фильтрацией по дате, названию, локации и пагинацией
@router.get("")
@cache(expire=10)
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    location: str | None = Query(None, description="Локация отеля (необязательно)"),
    title: str | None = Query(None, description="Название отеля (необязательно)"),
    date_from: date = Query(example="2025-01-01"),
    date_to: date = Query(example="2025-08-10"),
):
    try:
        per_page = pagination.per_page or 5
        return await db.hotels.get_filtered_by_time(
            date_from=date_from,
            date_to=date_to,
            location=location,
            title=title,
            limit=per_page,
            offset=per_page * (pagination.page - 1),
        )
    except (InvalidDateRangeException, NoHotelsFoundException) as ex:
        raise HTTPException(status_code=400, detail=ex.detail)


# Получение конкретного отеля по ID
@router.get("/{hotel_id}")
async def get_hotel(
    hotel_id: int,
    db: DBDep,
):
    return await db.hotels.get_one_or_none(id=hotel_id)


# Создание нового отеля
@router.post("")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Sochi",
                "value": {"title": "Отель Сочи 5 звезд у моря", "location": "sochi_u_morya"},
            },
            "2": {
                "summary": "Dubai",
                "value": {"title": "Отель Дубай 5 у фонтана", "location": "dubai_fountain"},
            },
        }
    ),
):
    hotel = await db.hotels.add(hotel_data)
    await db.commit()
    return {"status": "OK", "data": hotel}


# Полное обновление данных об отеле (PUT)
@router.put("/{hotel_id}")
async def edit_hotel(
    hotel_id: int,
    hotel_data: HotelAdd,
    db: DBDep,
):
    await db.hotels.edit(hotel_data, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


# Частичное обновление данных об отеле (PATCH)
@router.patch("/{hotel_id}")
async def partially_edit_hotel(
    hotel_id: int,
    hotel_data: HotelPatch,
    db: DBDep,
):
    await db.hotels.edit(hotel_data, exclude_unset=True, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


# Удаление отеля
@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int, db: DBDep):
    await db.hotels.delete(id=hotel_id)
    await db.commit()
    return {"status": "OK"}
