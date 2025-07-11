from datetime import date
from sqlalchemy import select, func
from src.models.rooms import RoomsOrm
from src.models.bookings import BookingsOrm


# Функция возвращает SQL-запрос, который выбирает ID свободных комнат
def rooms_ids_for_booking(
    date_from: date,
    date_to: date,
    hotel_id: int | None = None,
):
    # Подсчёт количества бронирований по комнатам, пересекающих заданные даты
    rooms_count = (
        select(BookingsOrm.room_id, func.count("*").label("rooms_booked"))
        .filter(
            BookingsOrm.date_from <= date_to,   # Заезд до конца выбранного периода
            BookingsOrm.date_to >= date_from,   # Выезд после начала периода
        )
        .group_by(BookingsOrm.room_id)
        .cte(name="rooms_count")  # Временная таблица
    )

    # Вычисляем количество оставшихся комнат (quantity - rooms_booked)
    rooms_left_table = (
        select(
            RoomsOrm.id.label("room_id"),
            (RoomsOrm.quantity - func.coalesce(rooms_count.c.rooms_booked, 0)).label("rooms_left"),
        )
        .outerjoin(rooms_count, RoomsOrm.id == rooms_count.c.room_id)
        .cte(name="rooms_left_table")
    )

    # Фильтрация по отелю (если указан hotel_id)
    rooms_ids_for_hotel = select(RoomsOrm.id)
    if hotel_id is not None:
        rooms_ids_for_hotel = rooms_ids_for_hotel.filter_by(hotel_id=hotel_id)
    rooms_ids_for_hotel = rooms_ids_for_hotel.subquery(name="rooms_ids_for_hotel")

    # Финальный запрос: только те комнаты, где осталось > 0 мест и они принадлежат нужному отелю
    rooms_ids_to_get = (
        select(rooms_left_table.c.room_id)
        .filter(
            rooms_left_table.c.rooms_left > 0,
            rooms_left_table.c.room_id.in_(rooms_ids_for_hotel),
        )
    )

    return rooms_ids_to_get  # Возвращается именно SQL-запрос, не результат
