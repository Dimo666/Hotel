from typing import Annotated
from fastapi import Depends, Query, HTTPException, Request
from pydantic import BaseModel

from src.database import async_session_maker
from src.services.auth import AuthService
from src.utils.db_manager import DBManager


# Параметры пагинации, автоматически извлекаются из query-параметров (?page=1&per_page=20)
class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1)]  # По умолчанию страница 1
    per_page: Annotated[int | None, Query(None, ge=1, lt=30)]  # Ограничение на размер страницы


# Тип-зависимость для внедрения пагинации
PaginationDep = Annotated[PaginationParams, Depends()]


# Получение access_token из cookies
def get_token(request: Request) -> str:
    token = request.cookies.get("access_token", None)
    if not token:
        raise HTTPException(status_code=401, detail="Вы не предоставили токен доступа")
    return token


# Раскодировка токена и получение user_id
def get_current_user_id(token: str = Depends(get_token)) -> int:
    data = AuthService().decode_token(token)  # ⚠️ должно быть decode_token, если ты хочешь извлечь payload
    return data["user_id"]


# Тип-зависимость: user_id, извлечённый из токена
UserIdDep = Annotated[int, Depends(get_current_user_id)]


# Создание DBManager с нужной фабрикой сессий
def get_db_manager():
    return


# Асинхронный зависимый генератор для работы с БД
async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


# Тип-зависимость: доступ к БД (внутри есть .users, .rooms и т.п.)
DBDep = Annotated[DBManager, Depends(get_db)]
