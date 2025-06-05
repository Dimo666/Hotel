# Импортируем нужные классы и функции из FastAPI
from fastapi import HTTPException
from fastapi import APIRouter, Response

from src.api.dependencies import UserIdDep, DBDep
# Импортируем фабрику для создания асинхронных сессий с базой данных
from src.database import async_session_maker

# Импортируем репозиторий пользователей, через который идёт работа с таблицей Users
from src.repositories.users import UsersRepository

# Импортируем схемы для валидации данных пользователя (pydantic-модели)
from src.schemas.users import UserRequestAdd, UserAdd

# Импортируем сервис для работы с аутентификацией (хеширование пароля, создание токена)
from src.services.auth import AuthService

# Создаём роутер с префиксом "/auth" и тегом для документации
router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


# Обработчик запроса POST /auth/login
@router.post("/login")
async def login_user(
        data: UserRequestAdd,  # Получаем данные от пользователя (email и пароль)
        response: Response,    # Объект ответа для установки cookie
        db: DBDep
):

    # Получаем пользователя по email вместе с хешированным паролем
    user = await db.users.get_user_with_hashed_password(email=data.email)

    # Если пользователь не найден — выбрасываем ошибку 401 (Unauthorized)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь с таким email не зарегистрирован")

    # Проверяем, совпадает ли введённый пароль с хешированным паролем в базе
    if not AuthService().verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Пароль неверный")

    # Генерируем access-токен на основе ID пользователя
    access_token = AuthService().create_access_token({"user_id": user.id})

    # Устанавливаем токен в cookie ответа
    response.set_cookie("access_token", access_token)

    # Возвращаем токен в теле ответа
    return {"access_token": access_token}


# Обработчик запроса POST /auth/register
@router.post("/register")
async def register_user(
        data: UserRequestAdd,  # Получаем данные от пользователя для регистрации
        db: DBDep
):
    # Хешируем пароль для безопасности (никогда не храним пароли в открытом виде!)
    hashed_password = AuthService().pwd_context.hash(data.password)

    # Создаём объект для нового пользователя
    new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)


    # Добавляем нового пользователя через репозиторий
    await db.users.add(new_user_data)
    # Подтверждаем изменения в базе данных
    await db.commit()

    # Возвращаем успешный ответ
    return {"status": "OK"}


# Обработчик запроса GET /auth/only_auth
@router.get("/me")
async def get_me(
        user_id: UserIdDep,
        db: DBDep,
):
    user = await db.users.get_one_or_none(id=user_id)
    return user


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie(key="access_token")
    return {"status": "Вы вышли из системы"}

