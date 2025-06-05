from fastapi import APIRouter, HTTPException  # импортируем схемы

from src.api.dependencies import DBDep, UserIdDep
from src.models.rooms import RoomsOrm
from src.schemas.bookings import BookingsCreate, BookingsRead, BookingsDBCreate

# Создаём роутер с префиксом /hotels, все маршруты будут начинаться с ним.
# Также указываем теги, чтобы в документации FastAPI они группировались.
router = APIRouter(prefix="/bookings", tags=["Бронирование"])

@router.post("", response_model=BookingsRead)
async def create_booking(
    booking_data: BookingsCreate,
    db: DBDep,
    user_id: UserIdDep,
):
    room = await db.rooms.get_by_id(booking_data.room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")

    booking = await db.bookings.add(BookingsDBCreate(
        **booking_data.model_dump(),
        user_id=user_id,
        price=room.price
    ))
    await db.commit()
    return booking
