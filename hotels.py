from fastapi import APIRouter, Query, Body  # импортируем класс APIRouter из fastapi

from dependencies import PaginationDep
from shemas.hotels import Hotel, HotelPatch  # импортируем схемы

# Создаём роутер с префиксом /hotels, все маршруты будут начинаться с ним.
# Также указываем теги, чтобы в документации FastAPI они группировались.
router = APIRouter(prefix="/hotels", tags=["Отели"])

# Временное хранилище отелей (имитация базы данных)
hotels = [
     {"id": 1, "title": "Sochi", "name": "sochi"},
     {"id": 2, "title": "Дубай", "name": "dubai"},
     {"id": 3, "title": "Мальдивы", "name": "maldivi"},
     {"id": 4, "title": "Геленджик", "name": "gelendzhik"},
     {"id": 5, "title": "Москва", "name": "moscow"},
     {"id": 6, "title": "Казань", "name": "kazan"},
     {"id": 7, "title": "Санкт-Петербург", "name": "spb"},
]


# Маршрут для получения списка отелей с фильтрацией по id и title (названию).
# Маршрут для получения списка отелей с фильтрацией и пагинацией
from fastapi import Query

# Маршрут для получения списка отелей с фильтрацией и пагинацией
@router.get("")
def get_hotels(
    pagination: PaginationDep,
    id: int | None = Query(None, description="Айдишник отеля (необязательный)"),
    title: str | None = Query(None, description="Название отеля (необязательное)"),
):
    # Фильтрация отелей по id и title, если они указаны
    hotels_ = []  # сюда складываются подходящие отели
    for hotel in hotels:
        if id and hotel["id"] != id:  # если указан id и он не совпадает — пропускаем
            continue
        if title and hotel["title"] != title:  # если указано название и оно не совпадает — пропускаем
            continue
        hotels_.append(hotel)  # добавляем подходящий отель в список

    if pagination.page and pagination.per_page:
        return hotels_[pagination.per_page * pagination.page - 1:][:pagination.per_page]
    return hotels_

# /hotels?page=1&per_page=2 - первая страница с двумя отелями


# Маршрут для создания нового отеля (POST-запрос).
@router.post("")
def create_hotel(hotel_data: Hotel = Body(openapi_examples={
    "1": {"summary": "Sochi", "value": {
        "title": "Отель Сочи 5 звезд у моря",
        "name": "sochi_u_morya"
    }},
    "2": {"summary": "Dubai", "value": {
            "title": "Отель Дубай 5 у фонтана",
            "name": "dubai_fountain"
    }},
})
):
    global hotels
    # Добавляем новый отель в список, назначая ему id на 1 больше последнего
    hotels.append({
        "id": hotels[-1]["id"] + 1,
        "title": hotel_data.title,
        "name": hotel_data.name
    })
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
