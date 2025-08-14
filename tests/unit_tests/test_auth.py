from src.services.auth import AuthService


# Юнит-тест для метода create_access_token()
def test_create_access_token():
    data = {"user_id": 1}  # Тестовые данные (payload)

    jwt_token = AuthService().create_access_token(data)  # Генерация токена

    assert jwt_token  # Проверяем, что токен не пустой
    assert isinstance(jwt_token, str)  # Проверяем, что токен — это строка
