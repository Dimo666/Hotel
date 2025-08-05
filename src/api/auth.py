# Импорты FastAPI
from fastapi import HTTPException, APIRouter, Response

# Зависимости — извлекают user_id из токена и создают доступ к БД
from src.api.dependencies import UserIdDep, DBDep
from src.exceptions import ObjectAlreadyExistsException

# Pydantic-схемы (валидация и сериализация данных)
from src.schemas.users import UserRequestAdd, UserAdd

# Сервис для работы с паролями и JWT
from src.services.auth import AuthService

# Создаём роутер с базовым префиксом
router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/login")
async def login_user(
    data: UserRequestAdd,       # Входные данные от пользователя (email и пароль)
    response: Response,         # Ответ, чтобы установить cookie
    db: DBDep,                  # Доступ к репозиториям
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
    user = await db.users.get_user_with_hashed_password(email=data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь с таким email не зарегистрирован")

    if not AuthService().verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Пароль неверный")

    access_token = AuthService().create_access_token({"user_id": user.id})
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
    hashed_password = AuthService().hash_password(data.password)
    new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)

    try:
        await db.users.add(new_user_data)
        await db.commit()
    except ObjectAlreadyExistsException:
        raise HTTPException(status_code=409, detail="Пользователь с такой почтой уже существует")

    return {"status": "OK"}


@router.get("/me")
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
    user = await db.users.get_one_or_none(id=user_id)
    return user


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

