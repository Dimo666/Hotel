from fastapi import APIRouter, Body
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilityAdd
from src.tasks.tasks import test_tasks  # Celery задача для теста

router = APIRouter(prefix="/facilities", tags=["Услуги"])


# Добавление новой услуги (удобства)
@router.post("")
async def create_facilities(
    db: DBDep,
    facility_data: FacilityAdd = Body()
):
    facility = await db.facilities.add(facility_data)  # Добавляем в БД
    await db.commit()                                  # Подтверждаем транзакцию

    test_tasks.delay()  # Запускаем фоновую задачу через Celery (необязательно)

    return {"status": "OK", "data": facility}


# Получение списка всех услуг с кэшированием (10 секунд)
@router.get("")
@cache(expire=10)
async def get_facilities(
    db: DBDep,
):
    print("ИДУ В БАЗУ ДАННЫХ")  # Выводим, если реально идём в БД (не из кэша)
    return await db.facilities.get_all()
