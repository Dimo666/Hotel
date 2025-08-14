from typing import Annotated
from fastapi import Depends, Query, Request
from pydantic import BaseModel

from src.database import async_session_maker
from src.exceptions import IncorrectTokenHTTPException, IncorrectTokenException, NoAccessTokenHTTPException
from src.services.auth import AuthService
from src.utils.db_manager import DBManager


# ⚙️ Параметры пагинации, автоматически парсятся из query (?page=1&per_page=20)
class PaginationParams(BaseModel):
    """
    Модель параметров пагинации.

    - page: номер страницы (по умолчанию 1, минимум 1)
    - per_page: сколько объектов на странице (необязательный, максимум 30)
    """

    page: Annotated[int | None, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(None, ge=1, lt=30)]


# 👇 Тип-зависимость для внедрения в ручки FastAPI
PaginationDep = Annotated[PaginationParams, Depends()]


# 🔐 Получение access_token из cookie
def get_token(request: Request) -> str:
    """
    Извлекает JWT токен из cookies.

    :raises HTTPException: если токен не найден
    :return: строка токена
    """
    token = request.cookies.get("access_token", None)
    if not token:
        raise NoAccessTokenHTTPException
    return token


# 🔓 Раскодировка токена и извлечение user_id
def get_current_user_id(token: str = Depends(get_token)) -> int:
    """
    Декодирует access_token и извлекает user_id из payload.

    :param token: JWT токен из cookie
    :return: user_id (int)
    """
    try:
        data = AuthService().decode_token(token)
    except IncorrectTokenException:
        raise IncorrectTokenHTTPException
    return data["user_id"]


# ✅ Тип-зависимость: user_id, извлечённый из токена
UserIdDep = Annotated[int, Depends(get_current_user_id)]


# 🗄️ Асинхронный генератор доступа к БД
async def get_db():
    """
    Асинхронный зависимый генератор для работы с БД.

    Используется в качестве Depends(), чтобы внутри ручек получить доступ к:
    db.users, db.hotels, db.rooms и т.д.

    :yield: DBManager (внутри открытая сессия)
    """
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


# 💾 Тип-зависимость: доступ к репозиториям через DBManager
DBDep = Annotated[DBManager, Depends(get_db)]
