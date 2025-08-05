import pytest

# ⚙️ Проверяем разные варианты регистрации и логина
@pytest.mark.parametrize("email, password, status_code", [
    ("k0t@pes.com", "1234", 200),     # ✅ валидные данные — ожидаем успешную регистрацию
    ("k0t@pes.com", "1234", 400),     # ❌ повторная регистрация того же email — ошибка
    ("k0t1@pes.com", "1235", 200),    # ✅ другой email — успешная регистрация
    ("abcde", "1235", 422),           # ❌ невалидный email — ошибка валидации
    ("abcde@abc", "1235", 422),       # ❌ невалидный email — ошибка валидации
])
async def test_auth_flow(email: str, password: str, status_code: int, ac):
    # 🟩 /auth/register — регистрация пользователя
    resp_register = await ac.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        }
    )
    assert resp_register.status_code == status_code

    # ⛔ Если регистрация не прошла (например, валидация или дубликат), дальше не продолжаем
    if status_code != 200:
        return

    # 🟩 /auth/login — логинимся под зарегистрированным пользователем
    resp_login = await ac.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        }
    )
    assert resp_login.status_code == 200
    assert ac.cookies["access_token"]                      # Проверяем, что access_token записан в куки
    assert "access_token" in resp_login.json()             # Токен также должен быть в теле ответа

    # 🟩 /auth/me — получаем текущего пользователя
    resp_me = await ac.get("/auth/me")
    assert resp_me.status_code == 200
    user = resp_me.json()
    assert user["email"] == email                          # Убедились, что это тот самый пользователь
    assert "id" in user                                    # У юзера есть id
    assert "password" not in user                          # Пароля быть не должно
    assert "hashed_password" not in user                   # И хэша пароля — тоже

    # 🟩 /auth/logout — выходим из системы
    resp_logout = await ac.post("/auth/logout")
    assert resp_logout.status_code == 200
    assert "access_token" not in ac.cookies                # После логаута токен должен исчезнуть
