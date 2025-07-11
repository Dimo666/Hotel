from src.services.auth import AuthService

# Тестируем создание и декодирование JWT токена
def test_decode_and_encode_token():
    data = {"user_id": 1}

    # Создание токена
    jwt_token = AuthService().create_access_token(data)
    assert jwt_token                  # Проверка, что токен создан
    assert isinstance(jwt_token, str)

    # Декодирование токена
    payload = AuthService().decode_token(jwt_token)
    assert payload                    # Проверка, что декодирование прошло успешно
    assert payload["user_id"] == data["user_id"]
