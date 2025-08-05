# ✅ Тест на создание бронирования
import pytest
from sqlalchemy import delete
from src.models import BookingsOrm as BookingModel



# Используем параметризацию: тест запускается несколько раз с разными входными данными
@pytest.mark.parametrize("room_id, date_from, date_to, status_code", [
    # Каждая строка — это отдельный тест-кейс
    (1, "2024-08-01", "2024-08-10", 200),  # Бронирование проходит успешно
    (1, "2024-08-02", "2024-08-11", 200),
    (1, "2024-08-03", "2024-08-12", 200),
    (1, "2024-08-04", "2024-08-13", 200),
    (1, "2024-08-05", "2024-08-14", 200),
    (1, "2024-08-06", "2024-08-15", 500),  # Ожидаем ошибку (например, пересечение дат)
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


@pytest.fixture(scope="function")
async def delete_all_bookings(db):
    await db.session.execute(delete(BookingModel))
    await db.commit()


@pytest.mark.parametrize("room_id, date_from, date_to, expected_count", [
    (1, "2024-08-01", "2024-08-05", 1),
    (1, "2024-08-10", "2024-08-12", 1),
    (1, "2024-08-15", "2024-08-18", 1),
])
async def test_add_and_get_bookings(
    room_id, date_from, date_to, expected_count,
    db, authenticated_ac, delete_all_bookings
):
    # ➕ Добавляем бронирование
    response = await authenticated_ac.post("/bookings", json={
        "room_id": room_id,
        "date_from": date_from,
        "date_to": date_to
    })
    assert response.status_code == 200

    # 📥 Получаем бронирования текущего пользователя
    me_response = await authenticated_ac.get("/bookings/me")
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["status"] == "OK"
    assert len(me_data["data"]) == expected_count
