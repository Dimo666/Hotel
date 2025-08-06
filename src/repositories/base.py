import logging
from asyncpg import UniqueViolationError
from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import NoResultFound, IntegrityError

from src.exceptions import ObjectNotFoundException, ObjectAlreadyExistsException
from src.repositories.mappers.base import DataMapper


class BaseRepository:
    """
    Базовый репозиторий для CRUD-операций с любой SQLAlchemy моделью.
    Используется во всех сервисах, чтобы не дублировать код.
    """

    model = None  # SQLAlchemy ORM-модель
    mapper: DataMapper = None  # Маппер ORM → Pydantic

    def __init__(self, session):
        """
        Инициализация репозитория с сессией SQLAlchemy.
        """
        self.session = session

    async def get_filtered(self, *filter, **filtered_by):
        """
        Получение списка записей по фильтрам.

        :param filter: SQLAlchemy фильтры
        :param filtered_by: именованные фильтры (например, id=1)
        :return: список Pydantic-моделей
        """
        query = select(self.model).filter(*filter).filter_by(**filtered_by)
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def get_all(self, *args, **kwargs):
        """
        Получение всех записей таблицы.
        """
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by):
        """
        Получение одного объекта или None по фильтру.

        :param filter_by: параметры фильтрации (например, id=1)
        :return: Pydantic-модель или None
        """
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def get_one(self, **filter_by):
        """
        Получение одного объекта по фильтру. Если не найден — исключение.

        :param filter_by: параметры фильтрации (например, id=1)
        :raises ObjectNotFoundException: если объект не найден
        :return: Pydantic-модель
        """
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except NoResultFound:
            raise ObjectNotFoundException
        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel):
        """
        Добавление нового объекта в БД.

        :param data: Pydantic-модель
        :raises ObjectAlreadyExistsException: при конфликте уникальности
        :return: созданный объект (Pydantic)
        """
        try:
            add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
            result = await self.session.execute(add_data_stmt)
            model = result.scalars().one()
            return self.mapper.map_to_domain_entity(model)
        except IntegrityError as ex:
            logging.error(f"Не удалось добавить данные в ББ, входные данные:{data} тип ошибки:{type(ex.orig.__cause__)=}")
            if isinstance(ex.orig.__cause__, UniqueViolationError):
                raise ObjectAlreadyExistsException from ex
            else:
                logging.error(f"Не знакомая ошибка: тип ошибки:{type(ex.orig.__cause__)=}")
                raise ex

    async def add_bulk(self, data: list[BaseModel]):
        """
        Массовое добавление объектов в БД.

        :param data: список Pydantic-моделей
        """
        add_data_stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(add_data_stmt)

    async def edit(self, data, exclude_unset: bool = False, **filter_by):
        """
        Обновление существующего объекта.

        :param data: Pydantic-модель с новыми данными
        :param exclude_unset: обновлять только переданные поля (для PATCH)
        :param filter_by: параметры для поиска объекта
        """
        await self.get_one_or_none(**filter_by)  # Проверка наличия
        edit_data_stmt = update(self.model).filter_by(**filter_by).values(**data.model_dump(exclude_unset=exclude_unset))
        await self.session.execute(edit_data_stmt)

    async def delete(self, **filter_by):
        """
        Удаление объекта по фильтру.

        :param filter_by: параметры фильтрации (например, id=1)
        """
        delete_stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stmt)
