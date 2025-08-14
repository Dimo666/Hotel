from datetime import date
from src.schemas.bookings import BookingAdd


# 🔁 Полный тест всех CRUD-операций над бронированием
async def test_booking_crud(db):
    # 📦 CREATE: создаём бронирование
    user_id = (await db.users.get_all())[0].id
    room_id = (await db.rooms.get_all())[0].id
    booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        date_from=date(2024, 8, 10),
        date_to=date(2024, 8, 20),
        price=100,
    )
    new_booking = await db.bookings.add(booking_data)

    # 🔍 READ: получаем бронь и проверяем, что она есть в БД
    booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert booking  # бронь найдена
    assert booking.id == new_booking.id
    assert booking.room_id == new_booking.room_id
    assert booking.user_id == new_booking.user_id
    # 💡 Альтернатива — сравниваем все поля, кроме id
    assert booking.model_dump(exclude={"id"}) == booking_data.model_dump()

    # ✏️ UPDATE: обновляем поле date_to
    updated_date = date(year=2024, month=8, day=25)
    update_booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        date_from=date(year=2024, month=8, day=10),
        date_to=updated_date,
        price=100,
    )
    await db.bookings.edit(update_booking_data, id=new_booking.id)

    # 🔁 Проверяем, что обновление применилось
    updated_booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert updated_booking
    assert updated_booking.id == new_booking.id
    assert updated_booking.date_to == updated_date  # поле обновлено

    # ❌ DELETE: удаляем бронь
    await db.bookings.delete(id=new_booking.id)

    # 🧪 Проверяем, что бронирование удалено
    booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert not booking  # должно быть None
