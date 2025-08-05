import pytest


@pytest.mark.asyncio
async def test_auth_flow(ac):
    # 1. Регистрируем нового юзера
    email = "flowtest@user.com"
    password = "flowpass"

    response = await ac.post("/auth/register", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200

    # 2. Логинимся и получаем токен
    response = await ac.post("/auth/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token

    # 3. Добавляем токен в заголовки и проверяем ручку /auth/me
    ac.headers.update({"Authorization": f"Bearer {token}"})
    response = await ac.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == email

    # 4. Выходим из системы
    response = await ac.post("/auth/logout")
    assert response.status_code == 200

    # 5. Пробуем снова обратиться к /auth/me — ожидаем 401
    response = await ac.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Вы не предоставили токен доступа"
