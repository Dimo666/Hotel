from src.schemas.hotels import HotelAdd  # Pydantic-схема для добавления отеля


# ✅ Асинхронный тест добавления нового отеля в базу данных
async def test_add_hotel(db):
    """
    Тестирует добавление отеля напрямую через репозиторий.

    :param db: тестовая сессия с доступом к hotel-репозиторию
    """
    # 🔹 Создаём тестовые данные отеля
    hotel_data = HotelAdd(title="Hotels 5 stars", location="San Francisco, CA")

    # 🔹 Добавляем отель в базу данных через репозиторий
    new_hotel_data = await db.hotels.add(hotel_data)

    # 🔹 Сохраняем изменения
    await db.commit()

    # 🔹 Проверка (в реальных тестах лучше использовать assert вместо print)
    assert new_hotel_data.id is not None
    assert new_hotel_data.title == hotel_data.title
    assert new_hotel_data.location == hotel_data.location

    print(f"{new_hotel_data=}")  # Можно временно оставить для отладки
