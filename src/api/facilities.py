from fastapi import APIRouter, Body

from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilityAdd
from src.tasks.tasks import test_tasks

router = APIRouter(prefix="/facilities", tags=["Услуги"])



@router.post("")
async def create_facilities(
    db: DBDep,
    facility_data: FacilityAdd = Body()
):

    facility = await db.facilities.add(facility_data)
    await db.commit()

    test_tasks.delay()

    return {"status": "OK", "data": facility}


@router.get("")
@cache(expire=10)
async def get_facilities(
        db: DBDep,
):
    print("ИДУ В БАЗУ ДАННЫХ")
    return await db.facilities.get_all()