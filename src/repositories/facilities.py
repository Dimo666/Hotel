from sqlalchemy import select, delete, insert

from src.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm  # ORM-модели
from src.repositories.base import BaseRepository  # Базовый репозиторий
from src.repositories.mappers.mappers import FacilityDataMapper  # Маппер ORM → доменная модель
from src.schemas.facilities import RoomFacility  # Pydantic-схема для связи комната-удобство


class FacilitiesRepository(BaseRepository):
    """
    Репозиторий для управления удобствами (Facilities).
    """

    model = FacilitiesOrm
    mapper = FacilityDataMapper


class RoomsFacilitiesRepository(BaseRepository):
    """
    Репозиторий для управления связью комнат и удобств (many-to-many).
    """

    model = RoomsFacilitiesOrm
    schema = RoomFacility

    async def set_room_facilities(self, room_id: int, facilities_ids: list[int]) -> None:
        """
        Устанавливает удобства для указанной комнаты:
        - удаляет неактуальные связи
        - добавляет новые, если их ещё нет

        :param room_id: ID комнаты
        :param facilities_ids: список ID удобств, которые должны быть связаны с комнатой
        :return: None
        """
        # Получаем текущие ID удобств, связанных с комнатой
        get_current_facilities_ids_query = select(self.model.facility_id).filter_by(room_id=room_id)
        res = await self.session.execute(get_current_facilities_ids_query)
        current_facilities_ids: list[int] = res.scalars().all()

        # Определяем, какие ID нужно удалить и какие — добавить
        ids_to_delete: list[int] = list(set(current_facilities_ids) - set(facilities_ids))
        ids_to_insert: list[int] = list(set(facilities_ids) - set(current_facilities_ids))

        # Удаляем устаревшие связи комната-удобство
        if ids_to_delete:
            delete_stmt = delete(self.model).filter(
                self.model.room_id == room_id,
                self.model.facility_id.in_(ids_to_delete),
            )
            await self.session.execute(delete_stmt)

        # Добавляем новые связи комната-удобство
        if ids_to_insert:
            insert_stmt = insert(self.model).values([{"room_id": room_id, "facility_id": f_id} for f_id in ids_to_insert])
            await self.session.execute(insert_stmt)
