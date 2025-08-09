from fastapi import APIRouter, Body
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep  # Зависимость — доступ к базе данных
from src.schemas.facilities import FacilityAdd  # Pydantic-схема для создания услуги
from src.services.facilities import FacilityService  # Сервис для работы с удобствами

router = APIRouter(prefix="/facilities", tags=["Услуги"])


@router.post("")
async def create_facilities(db: DBDep, facility_data: FacilityAdd = Body()):
    """
    Добавление новой услуги (удобства).

    :param db: Зависимость FastAPI — доступ к базе данных
    :param facility_data: Данные услуги (название)
    :return: Статус и созданная услуга
    """
    facility = await FacilityService(db).create_facility(facility_data)
    return {"status": "OK", "data": facility}


@router.get("")
@cache(expire=10)
async def get_facilities(db: DBDep):
    """
    Получение списка всех доступных услуг (удобств).
    Кэшируется на 10 секунд, чтобы уменьшить нагрузку на базу данных.

    :param db: Зависимость FastAPI — доступ к базе данных
    :return: Список всех удобств
    """
    print("ИДУ В БАЗУ ДАННЫХ")  # Для отладки — видно, когда не используется кэш
    return await FacilityService(db).get_facilities()
