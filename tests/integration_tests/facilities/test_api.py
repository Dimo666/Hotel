

async def test_get_facilities(ac):
    responses = await ac.get("/facilities",)

    assert responses.status_code == 200
    assert isinstance(responses.json(), list)


async def test_post_facilities(ac):
    facility_title = "Массаж"
    response = await ac.post("/facilities", json={"title": facility_title})
    assert response.status_code == 200
    res = response.json()
    assert isinstance(res, dict)
    assert res["data"]["title"] == facility_title
    assert "data" in res