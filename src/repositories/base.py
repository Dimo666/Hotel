# Импортируем базовую модель Pydantic
from pydantic import BaseModel

# Импортируем SQL-операторы для работы с базой данных
from sqlalchemy import select, insert, update, delete

# Импортируем HTTP-исключение для генерации ошибок API
from fastapi import HTTPException

# Импортируем исключение, которое возникает при нахождении нескольких результатов вместо одного
from sqlalchemy.exc import MultipleResultsFound


# Базовый репозиторий для работы с любыми моделями
class BaseRepository:
    # Переменные класса, которые потом будут переопределяться в наследниках
    model = None  # ORM-модель SQLAlchemy
    schema: BaseModel = None  # Pydantic-схема

    # При создании репозитория передаём ему активную сессию с базой данных
    def __init__(self, session):
        self.session = session

    # Метод для получения всех записей из таблицы
    async def get_all(self, *args, **kwargs):
        # Формируем запрос: SELECT * FROM model
        query = select(self.model)
        # Выполняем запрос
        result = await self.session.execute(query)
        # Преобразуем каждый результат из ORM в Pydantic-схему
        return [self.schema.model_validate(model) for model in result.scalars().all()]

    # Метод для получения одного объекта по фильтру или None
    async def get_one_or_none(self, **filter_by):
        # Формируем запрос с фильтрацией по переданным параметрам
        query = select(self.model).filter_by(**filter_by)
        # Выполняем запрос
        result = await self.session.execute(query)
        try:
            # Пробуем получить один результат или None
            model = result.scalars().one_or_none()
            if model is None:
                return None
            # Валидируем ORM-объект в Pydantic-модель
            return self.schema.model_validate(model)
        except MultipleResultsFound:
            # Если найдено несколько объектов — выбрасываем ошибку 400
            raise HTTPException(status_code=400, detail="Multiple objects found")

    # Метод для добавления нового объекта
    async def add(self, data: BaseModel):
        # Формируем запрос на вставку записи
        add_data_stmt = (
            insert(self.model)
            .values(**data.model_dump())  # Преобразуем Pydantic-объект в dict
            .returning(self.model)  # Возвращаем добавленный объект
        )
        result = await self.session.execute(add_data_stmt)
        model = result.scalars().one()
        return self.schema.model_validate(model)

    # Метод для редактирования объекта
    async def edit(self, data, exclude_unset: bool = False, **filter_by):
        # Проверяем, существует ли объект по фильтру
        obj = await self.get_one_or_none(**filter_by)

        if obj is None:
            # Если нет — ошибка 404
            raise HTTPException(status_code=404, detail="Object not found")

        # Формируем запрос на обновление данных
        edit_data_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))  # exclude_unset=True — обновить только переданные поля
        )

        await self.session.execute(edit_data_stmt)

    # Метод для удаления объекта
    async def delete(self, **filter_by):
        # Проверяем, существует ли объект
        obj = await self.get_one_or_none(**filter_by)

        if obj is None:
            # Если нет — ошибка 404
            raise HTTPException(status_code=404, detail="Object not found")

        # Формируем запрос на удаление
        delete_data_stmt = delete(self.model).filter_by(**filter_by)

        await self.session.execute(delete_data_stmt)

