from fastapi import APIRouter


from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddRequest, BookingAdd


router = APIRouter(prefix="/bookings", tags=["Бронирования"])


# Добавление бронирования (POST /bookings)
@router.post("")
async def add_booking(
    user_id: UserIdDep,              # Получаем user_id из токена (авторизованного пользователя)
    db: DBDep,                       # Зависимость для доступа к базе данных
    booking_data: BookingAddRequest # Данные, которые прислал клиент (room_id, даты)
):
    # Получаем объект комнаты по ID, чтобы узнать её цену
    room = await db.rooms.get_one_or_none(id=booking_data.room_id)

    # Получаем отель, к которому принадлежит комната (нужен для проверки доступности)
    hotel = await db.hotels.get_one_or_none(id=room.hotel_id)

    # Получаем цену комнаты
    room_price: int = room.price

    # Собираем полные данные для бронирования:
    # добавляем user_id и цену, а остальные поля берём из запроса
    _booking_data = BookingAdd(
        user_id=user_id,
        price=room_price,
        **booking_data.model_dump(),
    )

    # Добавляем бронирование с учётом доступности комнаты в отеле
    booking = await db.bookings.add_booking(_booking_data, hotel_id=hotel.id)

    # Сохраняем изменения в базе
    await db.commit()

    # Возвращаем успешный ответ с данными о бронировании
    return {"status": "OK", "data": booking}



# Получение всех бронирований (GET /bookings) — для админов
@router.get("")
async def get_bookings(
    db: DBDep,
):
    return await db.bookings.get_all()


# Получение бронирований текущего пользователя (GET /bookings/me)
@router.get("/me")
async def get_me(
    db: DBDep,
    user_id: UserIdDep,
):
    bookings = await db.bookings.get_filtered(user_id=user_id)
    return {"status": "OK", "data": bookings}
