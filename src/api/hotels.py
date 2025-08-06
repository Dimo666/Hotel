from datetime import date
from fastapi_cache.decorator import cache
from fastapi import APIRouter, Body, Query
from src.api.dependencies import PaginationDep, DBDep
from src.exceptions import check_dete_to_after_date_from, ObjectNotFoundException, HotelNotFoundException
from src.schemas.hotels import HotelPatch, HotelAdd

# Роутер для работы с отелями
router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("")
@cache(expire=10)
async def get_hotels(
    pagination: PaginationDep,  # Параметры пагинации: страница и кол-во элементов
    db: DBDep,  # Доступ к базе данных
    location: str | None = Query(None, description="Локация отеля (необязательно)"),
    title: str | None = Query(None, description="Название отеля (необязательно)"),
    date_from: date = Query(example="2025-01-01"),
    date_to: date = Query(example="2025-08-10"),
):
    """
    Получение списка отелей по фильтрам: локация, название, дата, пагинация.

    - Кэшируется на 10 секунд
    - Проверяет корректность диапазона дат
    - Проводит фильтрацию на уровне базы данных

    :param pagination: пагинация (страница и количество на страницу)
    :param db: доступ к репозиториям
    :param location: фильтрация по локации (необязательная)
    :param title: фильтрация по названию (необязательная)
    :param date_from: дата начала периода
    :param date_to: дата конца периода
    :return: список подходящих отелей
    """
    check_dete_to_after_date_from(date_from, date_to)  # Проверка дат
    per_page = pagination.per_page or 5
    return await db.hotels.get_filtered_by_time(
        date_from=date_from,
        date_to=date_to,
        location=location,
        title=title,
        limit=per_page,
        offset=per_page * (pagination.page - 1),
    )


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int, db: DBDep):
    """
    Получение одного отеля по ID.

    :param hotel_id: идентификатор отеля
    :param db: доступ к базе данных
    :raises HotelNotFoundException: если отель не найден
    :return: объект отеля
    """
    try:
        return await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundException


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
    """
    Создание нового отеля.

    :param db: доступ к БД
    :param hotel_data: входные данные отеля
    :return: статус и созданный объект
    """
    hotel = await db.hotels.add(hotel_data)
    await db.commit()
    return {"status": "OK", "data": hotel}


@router.put("/{hotel_id}")
async def edit_hotel(
    hotel_id: int,
    hotel_data: HotelAdd,
    db: DBDep,
):
    """
    Полное обновление информации об отеле (PUT).

    :param hotel_id: ID отеля
    :param hotel_data: новые данные (все поля обязательны)
    :param db: доступ к базе данных
    :return: статус
    """
    await db.hotels.edit(hotel_data, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.patch("/{hotel_id}")
async def partially_edit_hotel(
    hotel_id: int,
    hotel_data: HotelPatch,
    db: DBDep,
):
    """
    Частичное обновление информации об отеле (PATCH).

    :param hotel_id: ID отеля
    :param hotel_data: только изменяемые поля (необязательные)
    :param db: доступ к базе данных
    :return: статус
    """
    await db.hotels.edit(hotel_data, exclude_unset=True, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int, db: DBDep):
    """
    Удаление отеля по ID.

    :param hotel_id: ID удаляемого отеля
    :param db: доступ к базе данных
    :return: статус удаления
    """
    await db.hotels.delete(id=hotel_id)
    await db.commit()
    return {"status": "OK"}
