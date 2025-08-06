import pytest

# ✅ Тестирование полного сценария регистрации, логина и выхода пользователя
@pytest.mark.parametrize("email, password, status_code", [
    ("k0t@pes.com", "1234", 200),     # Валидная регистрация
    ("k0t@pes.com", "1234", 409),     # Повторная регистрация — конфликт
    ("k0t1@pes.com", "1235", 200),    # Новая регистрация — успех
    ("abcde", "1235", 422),           # Невалидный email (нет @)
    ("abcde@abc", "1235", 422),       # Невалидный email (нет домена)
])
async def test_auth_flow(email: str, password: str, status_code: int, ac):
    """
    Полный тест аутентификационного потока:
    регистрация → логин → /me → logout.

    :param email: тестовый email пользователя
    :param password: тестовый пароль
    :param status_code: ожидаемый результат регистрации
    :param ac: авторизованный HTTP-клиент (интеграционный тест)
    """

    # 🔹 1. Регистрация пользователя
    resp_register = await ac.post("/auth/register", json={"email": email, "password": password})
    assert resp_register.status_code == status_code

    # ⛔ Если регистрация не удалась, прекращаем тест
    if status_code != 200:
        return

    # 🔹 2. Логин пользователя
    resp_login = await ac.post("/auth/login", json={"email": email, "password": password})
    assert resp_login.status_code == 200
    assert "access_token" in resp_login.json()                   # Токен в теле ответа
    assert ac.cookies.get("access_token") is not None            # Токен в куках

    # 🔹 3. Получение текущего пользователя
    resp_me = await ac.get("/auth/me")
    assert resp_me.status_code == 200
    user = resp_me.json()
    assert user["email"] == email                                # Email совпадает
    assert "id" in user                                           # Есть ID
    assert "password" not in user                                 # Открытого пароля быть не должно
    assert "hashed_password" not in user                          # И хэша пароля тоже

    # 🔹 4. Выход из системы
    resp_logout = await ac.post("/auth/logout")
    assert resp_logout.status_code == 200
    assert "access_token" not in ac.cookies                       # Токен удалён из куков
