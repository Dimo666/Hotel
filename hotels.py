from fastapi import APIRouter, Body, Query
from pydantic import BaseModel

# Создаём роутер с префиксом /hotels, все маршруты будут начинаться с него.
# Также указываем теги, чтобы в документации FastAPI они группировались.
router = APIRouter(prefix="/hotels", tags=["Отели"])

# Временное хранилище отелей (имитация базы данных)
hotels = [
    {"id": 1, "title": "Sochi", "name": "sochi"},
    {"id": 2, "title": "Dubai", "name": "dubai"},
]

# Маршрут для получения списка отелей с фильтрацией по id и title (названию).
@router.get("")
def get_hotels(
    id: int | None = Query(None, description="Айдишник"),  # можно передать айди отеля
    title: str | None = Query(None, description="Название отеля")  # или название
):
    hotels_ = []  # сюда будем складывать отфильтрованные отели
    for hotel in hotels:
        if id and hotel["id"] != id:  # если указан id и он не совпадает — пропускаем
            continue
        if title and hotel["title"] != title:  # если указано название и оно не совпадает — пропускаем
            continue
        hotels_.append(hotel)  # добавляем подходящий отель в результат
    return hotels_

# Схема данных, которая описывает структуру входящих данных отеля.
class Hotel(BaseModel):
    title: str  # отображаемое название
    name: str   # внутреннее имя (например, slug)

# Маршрут для создания нового отеля (POST-запрос).
@router.post("")
def create_hotel(hotel_data: Hotel):
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
    name: str | None = Body(None),   # новое значение name (необязательно)
    title: str | None = Body(None)   # новое значение title (необязательно)
):
    global hotels
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            if title is not None:
                hotel["title"] = title
            if name is not None:
                hotel["name"] = name
            return {"status": "OK"}
    return {"error": "Hotel not found"}

# Маршрут для удаления отеля по id (DELETE-запрос).
@router.delete("/{hotel_id}")
def delete_hotel(hotel_id: int):
    global hotels
    # Фильтруем список, оставляя только те отели, у которых id не совпадает
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {"status": "OK"}
