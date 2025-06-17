from fastapi import APIRouter, Body

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilityAdd

router = APIRouter(prefix="/facilities", tags=["Услуги"])



@router.post("")
async def create_facilities(
    db: DBDep,
    facility_data: FacilityAdd = Body()
):

    facility = await db.facilities.add(facility_data)
    await db.commit()

    return {"status": "OK", "data": facility}


@router.get("")
async def get_facilities(
        db: DBDep,
):
    return await db.facilities.get_all()