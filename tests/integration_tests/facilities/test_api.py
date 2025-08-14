# ✅ Тест на получение списка удобств (GET /facilities)
async def test_get_facilities(ac):
    # Отправляем GET-запрос на ручку /facilities
    responses = await ac.get("/facilities")

    # Проверяем, что запрос прошёл успешно
    assert responses.status_code == 200

    # Проверяем, что в ответе — список удобств
    assert isinstance(responses.json(), list)


# ✅ Тест на добавление нового удобства (POST /facilities)
async def test_post_facilities(ac):
    facility_title = "Массаж"

    # Отправляем POST-запрос с новым названием удобства
    response = await ac.post("/facilities", json={"title": facility_title})

    # Проверяем успешность запроса
    assert response.status_code == 200

    # Проверяем структуру и содержимое ответа
    res = response.json()
    assert isinstance(res, dict)  # Ответ — словарь
    assert res["data"]["title"] == facility_title  # Название соответствует отправленному
    assert "data" in res  # Есть поле "data"
    assert res["status"] == "OK"  # Статус успешный
