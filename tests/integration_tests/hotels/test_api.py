# ✅ Тест получения списка отелей по диапазону дат
async def test_get_hotels(ac):
    """
    Тестирует эндпоинт GET /hotels:
    проверяет, что возвращается список отелей в заданном диапазоне дат.

    :param ac: HTTP-клиент (async_client) для выполнения запроса
    """
    # 🔹 Отправляем GET-запрос с параметрами дат
    response = await ac.get(
        "/hotels",
        params={
            "date_from": "2025-08-01",
            "date_to": "2025-08-10"
        }
    )

    # 🔹 Проверяем, что запрос выполнен успешно
    assert response.status_code == 200

    # 🔹 Убедимся, что в ответе — список
    assert isinstance(response.json(), list)
