# Импорты FastAPI
from fastapi import HTTPException, APIRouter, Response

# Зависимости — извлекают user_id из токена и создают доступ к БД
from src.api.dependencies import UserIdDep, DBDep


# Pydantic-схемы (валидация и сериализация данных)
from src.schemas.users import UserRequestAdd, UserAdd

# Сервис для работы с паролями и JWT
from src.services.auth import AuthService

# Создаём роутер с базовым префиксом
router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


# Вход пользователя (POST /auth/login)
@router.post("/login")
async def login_user(
    data: UserRequestAdd,  # email и пароль от пользователя
    response: Response,  # нужен для установки cookie
    db: DBDep,  # зависимость — доступ к репозиториям
):
    # Ищем пользователя по email
    user = await db.users.get_user_with_hashed_password(email=data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь с таким email не зарегистрирован")

    # Проверка пароля
    if not AuthService().verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Пароль неверный")

    # Генерация JWT
    access_token = AuthService().create_access_token({"user_id": user.id})

    # Установка токена в cookie
    response.set_cookie("access_token", access_token)

    return {"access_token": access_token}


# Регистрация пользователя (POST /auth/register)
@router.post("/register")
async def register_user(
    data: UserRequestAdd,  # email и пароль
    db: DBDep,
):
    try:
        hashed_password = AuthService().pwd_context.hash(data.password)  # Хешируем пароль
        new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)  # Создаём схему для создания пользователя
        await db.users.add(new_user_data)  # Добавляем в базу
        await db.commit()
    except:  # noqa: E722
        raise HTTPException(status_code=400)

    return {"status": "OK"}


# Получение текущего пользователя по JWT-токену (GET /auth/me)
@router.get("/me")
async def get_me(
    user_id: UserIdDep,  # вытаскивается из JWT токена
    db: DBDep,
):
    user = await db.users.get_one_or_none(id=user_id)
    return user


# Выход пользователя (удаление токена из cookie)
@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie(key="access_token")
    return {"status": "Вы вышли из системы"}
