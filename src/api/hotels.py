from datetime import date

from fastapi_cache.decorator import cache

from fastapi import APIRouter, Body, Query  # импортируем класс APIRouter из fastapi
from src.api.dependencies import PaginationDep, DBDep
from src.schemas.hotels import Hotel, HotelPatch, HotelAdd  # импортируем схемы

# Создаём роутер с префиксом /hotels, все маршруты будут начинаться с ним.
# Также указываем теги, чтобы в документации FastAPI они группировались.
router = APIRouter(prefix="/hotels", tags=["Отели"])


# Маршрут для получения списка отелей с фильтрацией и пагинацией
@router.get("")
@cache(expire=10)
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    location: str | None = Query(None, description="Локация отеля (необязательный)"),
    title: str | None = Query(None, description="Название отеля (необязательное)"),
    date_from: date = Query(example="2025-01-01"),
    date_to: date = Query(example="2025-08-10"),
):
    per_page = pagination.per_page or 5
    return await db.hotels.get_filtered_by_time(
        date_from=date_from,
        date_to=date_to,
        location=location,
        title=title,
        limit=per_page,
        offset=per_page * (pagination.page - 1)
    )



@router.get("/{hotel_id}")
async def get_hotel(
        hotel_id: int,
        db: DBDep,
):
    return await db.hotels.get_one_or_none(
        id=hotel_id,
    )


# Маршрут для создания нового отеля (POST-запрос).
@router.post("")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Sochi",
                "value": {
                    "title": "Отель Сочи 5 звезд у моря",
                    "location": "sochi_u_morya",
                },
            },
            "2": {
                "summary": "Dubai",
                "value": {
                    "title": "Отель Дубай 5 у фонтана",
                    "location": "dubai_fountain",
                },
            },
        }
    )
):

    hotel = await db.hotels.add(hotel_data)
    await db.commit()

    return {"status": "OK", "data": hotel}



# Маршрут для полного обновления данных об отеле по id (PUT-запрос).
@router.put("/{hotel_id}")
async def edit_hotel(
        hotel_id: int,
        hotel_data: HotelAdd,
        db: DBDep,

):

    await db.hotels.edit(hotel_data, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


# Маршрут для частичного обновления данных об отеле (PATCH-запрос).
@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле",
    description="Тут мы частично обновляем данные об отеле: можно отправить name, а можно title"
)
async def partially_edit_hotel(
    hotel_id: int,
    hotel_data: HotelPatch,  # новое значение title (необязательно)
    db: DBDep,
):
    await db.hotels.edit(hotel_data, exclude_unset=True, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


# Маршрут для удаления отеля по id (DELETE-запрос).
@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int, db: DBDep):
    await db.hotels.delete(id=hotel_id)
    await db.commit()
    return {"status": "OK"}
