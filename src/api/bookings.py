from fastapi import APIRouter
from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddRequest, BookingAdd


router = APIRouter(prefix="/bookings", tags=["Бронирования"])


# Добавление бронирования (POST /bookings)
@router.post("")
async def add_booking(
    user_id: UserIdDep,              # Получаем user_id из токена
    db: DBDep,                       # Зависимость — доступ к БД
    booking_data: BookingAddRequest # Входные данные от клиента
):
    room = await db.rooms.get_one_or_none(id=booking_data.room_id)  # Получаем цену комнаты
    room_price: int = room.price

    # Собираем полную схему для сохранения (добавляем user_id и цену)
    _booking_data = BookingAdd(
        user_id=user_id,
        price=room_price,
        **booking_data.model_dump(),
    )

    booking = await db.bookings.add_booking(_booking_data)  # Добавляем запись в БД
    await db.commit()
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
