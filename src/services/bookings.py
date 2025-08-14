from src.exceptions import ObjectNotFoundException, RoomNotFoundException
from src.schemas.bookings import BookingAddRequest, BookingAdd
from src.services.base import BaseService


class BookingService(BaseService):
    """
    Сервис для работы с бронированиями.

    Данный сервис включает методы для добавления бронирований, получения всех бронирований
    и получения бронирований конкретного пользователя.
    """

    async def add_booking(self, user_id: int, booking_data: BookingAddRequest):
        """
        Добавляет новое бронирование для пользователя.

        Этот метод выполняет проверку доступности комнаты и её цены, затем создает
        бронирование с переданными данными. Если комната не найдена, выбрасывается исключение.

        Args:
            user_id (int): ID авторизованного пользователя.
            booking_data (BookingAddRequest): Данные для бронирования, включая ID комнаты, даты.

        Returns:
            BookingAdd: Объект с данными добавленного бронирования.

        Raises:
            RoomNotFoundException: Если комната с указанным ID не найдена в базе.
            AllRoomsAreBookedException: Если все номера в отеле заняты.
        """
        try:
            room = await self.db.rooms.get_one(id=booking_data.room_id)  # Получаем объект комнаты по ID, чтобы узнать её цену
        except ObjectNotFoundException as ex:
            raise RoomNotFoundException from ex
        hotel = await self.db.hotels.get_one(id=room.hotel_id)  # Получаем отель, к которому принадлежит комната (нужен для проверки доступности)
        room_price: int = room.price  # Получаем цену комнаты
        # Собираем полные данные для бронирования:
        # добавляем user_id и цену, а остальные поля берём из запроса
        _booking_data = BookingAdd(
            user_id=user_id,
            price=room_price,
            **booking_data.model_dump(),
        )
        booking = await self.db.bookings.add_booking(_booking_data, hotel_id=hotel.id)  # Добавляем бронирование с учётом доступности комнаты в отеле
        await self.db.commit()  # Сохраняем изменения в базе
        return booking

    async def get_bookings(self):
        """
        Получает все бронирования.

        Этот метод возвращает список всех бронирований, доступных в системе.

        Returns:
            list: Список всех бронирований.
        """
        return await self.db.bookings.get_all()

    async def get_my_bookings(self, user_id: int):
        """
        Получает все бронирования текущего пользователя.

        Этот метод возвращает список бронирований, сделанных конкретным пользователем.

        Args:
            user_id (int): ID текущего пользователя.

        Returns:
            list: Список бронирований текущего пользователя.
        """
        return await self.db.bookings.get_filtered(user_id=user_id)
