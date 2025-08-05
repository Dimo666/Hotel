from datetime import date
from sqlalchemy import select, func
from src.models.rooms import RoomsOrm
from src.models.bookings import BookingsOrm


def rooms_ids_for_booking(
    date_from: date,
    date_to: date,
    hotel_id: int | None = None,
):
    """
    Возвращает SQL-запрос на выборку ID свободных комнат на указанный период.

    Комната считается свободной, если:
    - она не полностью забронирована в указанные даты;
    - относится к нужному отелю (если передан hotel_id).

    :param date_from: дата заезда
    :param date_to: дата выезда
    :param hotel_id: фильтрация по отелю (необязательно)
    :return: SQL-запрос (select), который можно использовать в других ORM-запросах
    """

    # Считаем количество бронирований по room_id, которые пересекаются с диапазоном дат
    rooms_count = (
        select(BookingsOrm.room_id, func.count("*").label("rooms_booked"))
        .filter(
            BookingsOrm.date_from <= date_to,  # Бронь начинается до окончания периода
            BookingsOrm.date_to >= date_from,  # Бронь заканчивается после начала периода
        )
        .group_by(BookingsOrm.room_id)
        .cte(name="rooms_count")  # Создаём CTE (временную таблицу)
    )

    # Вычисляем количество свободных мест по каждой комнате:
    # total_quantity - уже забронировано
    rooms_left_table = (
        select(
            RoomsOrm.id.label("room_id"),
            (RoomsOrm.quantity - func.coalesce(rooms_count.c.rooms_booked, 0)).label("rooms_left"),
        )
        .outerjoin(rooms_count, RoomsOrm.id == rooms_count.c.room_id)
        .cte(name="rooms_left_table")
    )

    # Фильтрация: получаем ID комнат для нужного отеля (если указан)
    rooms_ids_for_hotel = select(RoomsOrm.id)
    if hotel_id is not None:
        rooms_ids_for_hotel = rooms_ids_for_hotel.filter_by(hotel_id=hotel_id)
    rooms_ids_for_hotel = rooms_ids_for_hotel.subquery(name="rooms_ids_for_hotel")

    # Финальный SQL-запрос:
    # выбираем только те комнаты, у которых осталось > 0 мест и которые принадлежат нужному отелю
    rooms_ids_to_get = select(rooms_left_table.c.room_id).filter(
        rooms_left_table.c.rooms_left > 0,
        rooms_left_table.c.room_id.in_(rooms_ids_for_hotel),
    )

    return rooms_ids_to_get  # Возвращаем сам SQL-запрос (не выполняем его)

