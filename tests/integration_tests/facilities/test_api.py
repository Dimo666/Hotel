

async def test_get_facilities(ac):
    responses = await ac.get("/facilities",)
    print(f"{responses.json()=}")

    assert responses.status_code == 200


async def test_add_facility(ac):
    data = {"title": "Wi-Fi1"}
    response = await ac.post("/facilities", json=data)

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["status"] == "OK"
    assert response_json["data"]["title"] == "Wi-Fi1"