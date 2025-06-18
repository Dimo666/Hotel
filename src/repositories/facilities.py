from sqlalchemy import select, delete

from src.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm
from src.repositories.base import BaseRepository
from src.schemas.facilities import Facility, RoomFacility


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm
    schema = Facility


class RoomsFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesOrm
    schema = RoomFacility

    async def get_facility_ids_by_room(self, room_id: int) -> set[int]:
        query = select(self.model.facility_id).filter_by(room_id=room_id)
        result = await self.session.execute(query)
        return set(result.scalars().all())

    async def delete_by_room_and_facility_ids(self, room_id: int, facility_ids: list[int]):
        stmt = (
            delete(self.model)
            .where(self.model.room_id == room_id)
            .where(self.model.facility_id.in_(facility_ids))
        )
        await self.session.execute(stmt)