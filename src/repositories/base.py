from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete
from fastapi import HTTPException
from sqlalchemy.exc import MultipleResultsFound


class BaseRepository:
    model = None


    def __init__(self, session):
        self.session = session


    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()


    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            return result.scalars().one_or_none()
        except MultipleResultsFound:
            raise HTTPException(status_code=400, detail="Multiple objects found")


    async def add(self, data: BaseModel):
        add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(add_data_stmt)
        return result.scalars().one()


    async def edit(self, data, **filter_by):
        obj = await self.get_one_or_none(**filter_by)

        if obj is None:
            raise HTTPException(status_code=404, detail="Object not found")

        edit_data_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=True))
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(edit_data_stmt)


    async def delete(self, **filter_by):
        obj = await self.get_one_or_none(**filter_by)

        if obj is None:
            raise HTTPException(status_code=404, detail="Object not found")

        delete_data_stmt = (
            delete(self.model)
            .filter_by(**filter_by)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(delete_data_stmt)
