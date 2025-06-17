from fastapi import APIRouter

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilitiesAdd

router = APIRouter(prefix="/facilities", tags=["Услуги"])



@router.post("")
async def create_facilities(
    db: DBDep,
    facilities_data: FacilitiesAdd
):

    facilities = await db.facilities.add(facilities_data)
    await db.commit()

    return {"status": "OK", "data": facilities}


@router.get("")
async def get_facilities(
        db: DBDep,
):
    return await db.facilities.get_all()