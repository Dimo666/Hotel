from src.schemas.facilities import FacilityAdd
from src.services.base import BaseService
from src.tasks.tasks import test_task


class FacilityService(BaseService):
    """
    Сервис для управления удобствами (facilities) в отеле.
    """

    async def create_facility(self, data: FacilityAdd):
        """
        Создание нового удобства (например, Wi-Fi, кондиционер и т.д.).

        :param data: входные данные для создания удобства
        :return: созданный объект удобства
        """
        # Добавляем удобство в базу данных
        facility = await self.db.facilities.add(data)
        await self.db.commit()

        # Запускаем фоновую задачу (например, для логов или уведомлений)
        test_task.delay()  # type: ignore — отключаем проверку типов для Celery

        return facility

    async def get_facilities(self):
        return await self.db.facilities.get_all()
