from src.database import async_session_maker_null_pool  # Фабрика асинхронных сессий SQLAlchemy
from src.schemas.hotels import HotelAdd       # Pydantic-схема для добавления отеля
from src.utils.db_manager import DBManager    # Контекстный менеджер для работы с БД

# Асинхронный тест добавления отеля
async def test_add_hotel(db):
    # Создаём объект отеля на основе схемы HotelAdd
    hotel_data = HotelAdd(title="Hotels 5 stars", location="San Francisco, CA")

    # Добавляем отель в базу данных
    new_hotel_data = await db.hotels.add(hotel_data)

    await db.commit()

    # Выводим результат для проверки
    print(f"{new_hotel_data=}")
