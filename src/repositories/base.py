# Импортируем базовую модель Pydantic
from pydantic import BaseModel

# Импортируем SQL-операторы для работы с базой данных
from sqlalchemy import select, insert, update, delete

# Импортируем HTTP-исключение для генерации ошибок API
from fastapi import HTTPException

# Импортируем исключение, которое возникает при нахождении нескольких результатов вместо одного
from sqlalchemy.exc import MultipleResultsFound

from src.repositories.mappers.base import DataMapper


# Базовый репозиторий для работы с любыми моделями
class BaseRepository:
    # Переменные класса, которые потом будут переопределяться в наследниках
    model = None  # ORM-модель SQLAlchemy
    mapper: DataMapper = None

    # При создании репозитория передаём ему активную сессию с базой данных
    def __init__(self, session):
        self.session = session

    # Метод для получения всех записей из таблицы
    async def get_filtered(self, *filter, **filtered_by):
        query = (
            select(self.model)
            .filter(*filter)
            .filter_by(**filtered_by)
        ) # Формируем запрос: SELECT * FROM model с фильтрацией по указанным полям
        result = await self.session.execute(query) # Выполняем запрос в базе данных
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()] # Преобразуем каждый результат из ORM в Pydantic-схему

    # Асинхронный метод для получения всех записей без фильтрации
    async def get_all(self, *args, **kwargs):
        return await self.get_filtered()


    # Метод для получения одного объекта по фильтру или None
    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by) # Формируем запрос с фильтрацией по переданным параметрам
        result = await self.session.execute(query) # Выполняем запрос
        try:
            model = result.scalars().one_or_none()  # Пробуем получить один результат или None
            if model is None:
                return None
            return self.mapper.map_to_domain_entity(model) # Валидируем ORM-объект в Pydantic-модель
        except MultipleResultsFound:
            raise HTTPException(status_code=400, detail="Multiple objects found") # Если найдено несколько объектов — выбрасываем ошибку 400

    # Метод для добавления нового объекта
    async def add(self, data: BaseModel):
        add_data_stmt = (  # Формируем запрос на вставку записи
            insert(self.model)
            .values(**data.model_dump())  # Преобразуем Pydantic-объект в dict
            .returning(self.model)  # Возвращаем добавленный объект
        )
        result = await self.session.execute(add_data_stmt)
        model = result.scalars().one()
        return self.mapper.map_to_domain_entity(model)

        # Метод для добавления нового объекта
    async def add_bulk(self, data: list[BaseModel]):
        add_data_stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(add_data_stmt)

    # Метод для редактирования объекта
    async def edit(self, data, exclude_unset: bool = False, **filter_by):
        obj = await self.get_one_or_none(**filter_by)  # Проверяем, существует ли объект по фильтру

        if obj is None:
            raise HTTPException(status_code=404, detail="Object not found")  # Если нет — ошибка 404

        # Формируем запрос на обновление данных
        edit_data_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))  # exclude_unset=True — обновить только переданные поля
        )

        await self.session.execute(edit_data_stmt)

    # Метод для удаления объекта
    async def delete(self, **filter_by):
        obj = await self.get_one_or_none(**filter_by) # Проверяем, существует ли объект

        if obj is None:
            raise HTTPException(status_code=404, detail="Object not found") # Если нет — ошибка 404

        delete_data_stmt = delete(self.model).filter_by(**filter_by) # Формируем запрос на удаление

        await self.session.execute(delete_data_stmt)
