from fastapi import APIRouter, Body, Query  # импортируем класс APIRouter из fastapi
from sqlalchemy import insert, select

from src.api.dependencies import PaginationDep
from src.database import async_session_maker, engine
from src.models.hotels import HotelsOrm
from src.schemas.hotels import Hotel, HotelPatch  # импортируем схемы

# Создаём роутер с префиксом /hotels, все маршруты будут начинаться с ним.
# Также указываем теги, чтобы в документации FastAPI они группировались.
router = APIRouter(prefix="/hotels", tags=["Отели"])



@router.get("") # Маршрут для получения списка отелей с фильтрацией и пагинацией
async def get_hotels(
    pagination: PaginationDep,
    id: int | None = Query(None, description="Айдишник отеля (необязательный)"),
    title: str | None = Query(None, description="Название отеля (необязательное)"),
):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        query = select(HotelsOrm)
        if id:
            query = query.filter_by(id=id)
        if title:
            query = query.filter_by(title=title)
        query = (
            query
            .limit(per_page)
            .offset(per_page * (pagination.page - 1))
        )

        result = await session.execute(query)

        hotels = result.scalars().all()
        # print(type(hotels), hotels)
        return hotels


    # if pagination.page and pagination.per_page:
    #     return hotels_[pagination.per_page * pagination.page - 1:][:pagination.per_page]
    # return hotels_

# /hotels?page=1&per_page=2 - первая страница с двумя отелями


# Маршрут для создания нового отеля (POST-запрос).
@router.post("")
async def create_hotel(hotel_data: Hotel = Body(openapi_examples={
    "1": {"summary": "Sochi", "value": {
        "title": "Отель Сочи 5 звезд у моря",
        "location": "sochi_u_morya"
    }},
    "2": {"summary": "Dubai", "value": {
            "title": "Отель Дубай 5 у фонтана",
            "location": "dubai_fountain"
    }},
})
):
    async with async_session_maker() as session:
        add_hotel_stmt = insert(HotelsOrm).values(**hotel_data.model_dump())
        # print(add_hotel_stmt.compile(engine, compile_kwargs={"literal_binds": True}))
        await session.execute(add_hotel_stmt)
        await session.commit()

    return {"status": "OK"}

# Маршрут для полного обновления данных об отеле по id (PUT-запрос).
@router.put("/{hotel_id}")
def put_hotel(hotel_id: int, hotel_data: Hotel):
    global hotels
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            hotel["title"] = hotel_data.title
            hotel["name"] = hotel_data.name
            return {"status": "OK"}  # если нашли и обновили
    return {"error": "Hotel not found"}  # если не нашли отель

# Маршрут для частичного обновления данных об отеле (PATCH-запрос).
@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле",
    description="Тут мы частично обновляем данные об отеле: можно отправить name, а можно title"
)
def patch_hotel(
    hotel_id: int,
    hotel_data: HotelPatch,  # новое значение title (необязательно)
):
    global hotels
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            if hotel_data.title is not None:
                hotel["title"] = hotel_data.title
            if hotel_data.name is not None:
                hotel["name"] = hotel_data.name
            return {"status": "OK"}
    return {"error": "Hotel not found"}

# Маршрут для удаления отеля по id (DELETE-запрос).
@router.delete("/{hotel_id}")
def delete_hotel(hotel_id: int):
    global hotels
    # Фильтруем список, оставляя только те отели, у которых id не совпадает
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {"status": "OK"}
