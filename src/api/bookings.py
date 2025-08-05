from fastapi import APIRouter, HTTPException

from src.api.dependencies import DBDep, UserIdDep
from src.exceptions import ObjectNotFoundException, AllRoomsAreBookedException
from src.schemas.bookings import BookingAddRequest, BookingAdd


router = APIRouter(prefix="/bookings", tags=["Бронирования"])


"""
    Добавляет новое бронирование комнаты для текущего пользователя.

    Args:
        user_id (int): ID авторизованного пользователя.
        db (DBDep): Зависимость для доступа к базе данных.
        booking_data (BookingAddRequest): Данные о бронировании (room_id, даты).

    Returns:
        dict: Ответ с данными о бронировании или сообщение об ошибке.

    Raises:
        HTTPException: Если номер не найден или все номера в отеле заняты.
    """


@router.post("")
async def add_booking(
    user_id: UserIdDep,  # Получаем user_id из токена (авторизованного пользователя)
    db: DBDep,  # Зависимость для доступа к базе данных
    booking_data: BookingAddRequest,  # Данные, которые прислал клиент (room_id, даты)
):
    try:
        room = await db.rooms.get_one(id=booking_data.room_id)  # Получаем объект комнаты по ID, чтобы узнать её цену
    except ObjectNotFoundException:
        raise HTTPException(status_code=400, detail="Номер не найден")
    hotel = await db.hotels.get_one(id=room.hotel_id)  # Получаем отель, к которому принадлежит комната (нужен для проверки доступности)
    room_price: int = room.price  # Получаем цену комнаты
    # Собираем полные данные для бронирования:
    # добавляем user_id и цену, а остальные поля берём из запроса
    _booking_data = BookingAdd(
        user_id=user_id,
        price=room_price,
        **booking_data.model_dump(),
    )
    try:
        booking = await db.bookings.add_booking(_booking_data, hotel_id=hotel.id)  # Добавляем бронирование с учётом доступности комнаты в отеле
    except AllRoomsAreBookedException as ex:
        raise HTTPException(status_code=400, detail=ex.detail)
    await db.commit()  # Сохраняем изменения в базе
    return {"status": "OK", "data": booking}  # Возвращаем успешный ответ с данными о бронировании


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
