# ✅ Тест на создание бронирования
import pytest
from tests.conftest import get_db_null_pool


# Используем параметризацию: тест запускается несколько раз с разными входными данными
@pytest.mark.parametrize("room_id, date_from, date_to, status_code", [
    # Каждая строка — это отдельный тест-кейс
    (1, "2024-08-01", "2024-08-10", 200),  # Бронирование проходит успешно
    (1, "2024-08-02", "2024-08-11", 200),
    (1, "2024-08-03", "2024-08-12", 200),
    (1, "2024-08-04", "2024-08-13", 200),
    (1, "2024-08-05", "2024-08-14", 200),
    (1, "2024-08-06", "2024-08-15", 400),  # Ожидаем ошибку (например, пересечение дат)
    (1, "2024-08-17", "2024-08-25", 200),
])
async def test_add_booking(
        room_id, date_from, date_to, status_code,  # Параметры, передаваемые из списка выше
        db, authenticated_ac                       # Фикстуры: подключение к БД и авторизованный клиент
):
    # Отправляем POST-запрос на эндпоинт /bookings
    # room_id = (await db.rooms.get_all())[0].id
    response = await authenticated_ac.post(
        "/bookings",
        json={
            "room_id": room_id,      # Комната, которую хотим забронировать
            "date_from": date_from,  # Начало периода бронирования
            "date_to": date_to       # Конец периода бронирования
        }
    )

    # Проверяем, что код ответа соответствует ожидаемому
    assert response.status_code == status_code

    # Если всё прошло успешно, проверяем тело ответа
    if status_code == 200:
        res = response.json()
        assert isinstance(res, dict)          # Ответ должен быть в виде словаря
        assert res["status"] == "OK"          # Ожидаем статус OK
        assert "data" in res                  # Должны получить данные о бронировании


# Фикстура, которая очищает таблицу бронирований перед тестами
@pytest.fixture(scope="module")
async def delete_all_bookings():
    async for _db in get_db_null_pool():       # Получаем объект базы из генератора
        await _db.bookings.delete()            # Удаляем все записи (предполагается, что delete без аргументов удаляет всё)
        await _db.commit()                     # Подтверждаем изменения


# Тест проверяет, что после каждого нового бронирования растёт общее количество бронирований пользователя
@pytest.mark.parametrize("room_id, date_from, date_to, booked_rooms", [
    (1, "2024-08-01", "2024-08-10", 1),
    (1, "2024-08-02", "2024-08-11", 2),
    (1, "2024-08-03", "2024-08-12", 3),
])
async def test_add_and_get_my_bookings(
    room_id,
    date_from,
    date_to,
    booked_rooms,
    delete_all_bookings,    # Очищаем БД перед каждым тестом
    authenticated_ac,       # Авторизованный клиент
):
    # ➕ Создаём бронирование
    response = await authenticated_ac.post(
        "/bookings",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        }
    )
    assert response.status_code == 200

    # 🔍 Получаем список своих бронирований
    response_my_bookings = await authenticated_ac.get("/bookings/me")
    assert response_my_bookings.status_code == 200
    # ❗ Ошибка тут: ты сравниваешь `len(response.json())`, но `json()` — это словарь
    # Нужно так:
    data = response_my_bookings.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert len(data["data"]) == booked_rooms  # Сравниваем количество бронирований
