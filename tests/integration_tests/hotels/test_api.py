


async def test_get_hotels(ac):
    responses = await ac.get(
        "/hotels",
        params={
            "date_from": "2025-08-01",
            "date_to": "2025-08-10"
        }

    )
    print(f"{responses.json()=}")

    assert responses.status_code == 200
