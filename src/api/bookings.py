from fastapi import APIRouter

from src.api.dependencies import DBDep, UserIdDep
from src.exceptions import AllRoomsAreBookedException, AllRoomsAreBookedHTTPException
from src.schemas.bookings import BookingAddRequest
from src.services.bookings import BookingService

router = APIRouter(prefix="/bookings", tags=["Бронирования"])

"""
    Маршруты для работы с бронированиями.

    POST /bookings:
        Добавляет новое бронирование комнаты для текущего пользователя.

    GET /bookings:
        Получение всех бронирований (для администраторов).

    GET /bookings/me:
        Получение всех бронирований текущего пользователя.

    Args:
        user_id (int): ID авторизованного пользователя для маршрутов, связанных с пользователем.
        db (DBDep): Зависимость для доступа к базе данных.
        booking_data (BookingAddRequest): Данные о бронировании (room_id, даты).

    Returns:
        dict: Ответ с данными о бронировании или сообщение об ошибке для POST-запроса.
        list: Список всех бронирований или бронирований текущего пользователя для GET-запросов.

    Raises:
        HTTPException: 
            - Для маршрута POST /bookings если номер не найден или все номера в отеле заняты.
            - Для маршрута GET /bookings если возникают ошибки при получении данных из базы.
"""


@router.post("")
async def add_booking(
        user_id: UserIdDep,  # Получаем user_id из токена (авторизованного пользователя)
        db: DBDep,  # Зависимость для доступа к базе данных
        booking_data: BookingAddRequest,  # Данные, которые прислал клиент (room_id, даты)
):
    """
    Создает новое бронирование для текущего пользователя.

    В данном маршруте добавляется бронирование на указанную комнату с переданными датами.
    Если все номера заняты, будет выброшено исключение.

    Args:
        user_id (int): ID текущего пользователя.
        db (DBDep): Зависимость для доступа к базе данных.
        booking_data (BookingAddRequest): Данные о бронировании (ID комнаты, даты бронирования).

    Returns:
        dict: Статус ответа с данными о бронировании.

    Raises:
        HTTPException: Если номер не найден или все номера заняты.
    """
    try:
        booking = await BookingService(db).add_booking(user_id, booking_data)
    except AllRoomsAreBookedException:
        raise AllRoomsAreBookedHTTPException
    return {"status": "OK", "data": booking}  # Возвращаем успешный ответ с данными о бронировании


@router.get("")
async def get_bookings(db: DBDep):
    """
    Получает все бронирования (для администраторов).

    Этот маршрут позволяет администратору получить список всех бронирований.

    Args:
        db (DBDep): Зависимость для доступа к базе данных.

    Returns:
        list: Список всех бронирований.
    """
    return await BookingService(db).get_bookings()


@router.get("/me")
async def get_me(
        db: DBDep,
        user_id: UserIdDep,
):
    """
    Получает все бронирования текущего пользователя.

    Этот маршрут позволяет пользователю получить список своих бронирований.

    Args:
        db (DBDep): Зависимость для доступа к базе данных.
        user_id (int): ID текущего пользователя.

    Returns:
        dict: Список бронирований текущего пользователя.
    """
    bookings = await BookingService(db).get_my_bookings(user_id)
    return {"status": "OK", "data": bookings}
