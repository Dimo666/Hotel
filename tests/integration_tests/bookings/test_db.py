from datetime import date

from src.schemas.bookings import BookingAdd, BookingPatch


async def test_booking_crud(db):
    # CREATE
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

    # READ
    booking_from_db = await db.bookings.get_one_or_none(id=new_booking.id)
    assert booking_from_db is not None
    assert booking_from_db.price == 100

    # UPDATE
    await db.bookings.edit(
        data=BookingPatch(price=200),
        id=new_booking.id,
        exclude_unset=True
    )
    updated_booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert updated_booking.price == 200

    # DELETE
    await db.bookings.delete(id=new_booking.id)
    deleted_booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert deleted_booking is None

    await db.commit()
