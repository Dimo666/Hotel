# Импорты FastAPI
from fastapi import APIRouter, Response

# Зависимости — извлекают user_id из токена и создают доступ к БД
from src.api.dependencies import UserIdDep, DBDep
from src.exceptions import (
    EmailNotRegisteredException,
    EmailNotRegisteredHTTPException,
    IncorrectPasswordException,
    IncorrectPasswordHTTPException,
    UserAlreadyExistsException,
    UserEmailAlreadyExistsHTTPException,
)

# Pydantic-схемы (валидация и сериализация данных)
from src.schemas.users import UserRequestAdd

# Сервис для работы с паролями и JWT
from src.services.auth import AuthService

# Создаём роутер с базовым префиксом
router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/login")
async def login_user(
    data: UserRequestAdd,  # Входные данные от пользователя (email и пароль)
    response: Response,  # Ответ, чтобы установить cookie
    db: DBDep,  # Доступ к репозиториям
):
    """
    Авторизация пользователя.

    - Проверяет существование пользователя по email
    - Сравнивает хеш пароля
    - Генерирует JWT и устанавливает его в cookie

    :param data: email и пароль
    :param response: HTTP-ответ (для установки cookie)
    :param db: доступ к базе данных
    :raises HTTPException: если пользователь не найден или пароль неверный
    :return: access_token
    """
    try:
        access_token = await AuthService(db).login_user(data)
    except EmailNotRegisteredException:
        raise EmailNotRegisteredHTTPException
    except IncorrectPasswordException:
        raise IncorrectPasswordHTTPException

    response.set_cookie("access_token", access_token)
    return {"access_token": access_token}


@router.post("/register")
async def register_user(
    data: UserRequestAdd,  # email и пароль
    db: DBDep,
):
    """
    Регистрация нового пользователя.

    - Хеширует пароль
    - Добавляет нового пользователя в БД
    - Обрабатывает конфликт, если email уже существует

    :param data: email и пароль
    :param db: доступ к базе данных
    :raises HTTPException: если пользователь уже существует
    :return: статус OK
    """
    try:
        await AuthService(db).register_user(data)
    except UserAlreadyExistsException:
        raise UserEmailAlreadyExistsHTTPException

    return {"status": "OK"}


@router.get("/me", summary="👨‍💻Мой профиль")
async def get_me(
    user_id: UserIdDep,  # user_id берется из JWT
    db: DBDep,
):
    """
    Получение данных текущего пользователя по JWT.

    :param user_id: ID пользователя, извлечённый из токена
    :param db: доступ к базе данных
    :return: объект пользователя или None
    """
    return await AuthService(db).get_one_or_none(user_id)


@router.post("/logout")
async def logout_user(response: Response):
    """
    Выход пользователя.

    - Удаляет access_token из cookie

    :param response: HTTP-ответ
    :return: статус выхода
    """
    response.delete_cookie(key="access_token")
    return {"status": "Вы вышли из системы"}
