# ✅ Тест на создание бронирования
async def test_add_booking(db, authenticated_ac):
    # Получаем ID первой доступной комнаты из базы
    room_id = (await db.rooms.get_all())[0].id

    # Отправляем POST-запрос на ручку /bookings с нужными параметрами
    response = await authenticated_ac.post(
        "/bookings",
        json={
            "room_id": room_id,
            "date_from": "2024-08-01",
            "date_to": "2024-08-10",
        }
    )

    # Проверяем, что ответ успешный
    assert response.status_code == 200

    # Получаем JSON-ответ и проверяем его структуру
    res = response.json()
    assert isinstance(res, dict)              # Ответ должен быть словарём
    assert res["status"] == "OK"              # Ожидаем статус "OK"
    assert "data" in res                      # В ответе должен быть блок "data" с информацией о бронировании
