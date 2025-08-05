from typing import TypeVar

from pydantic import BaseModel

from src.database import Base

DBModelType = TypeVar("DBModelType", bound=Base)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class DataMapper:
    # Базовый класс маппера. Предназначен для наследования.

    db_model: type[DBModelType] = None  # Класс модели базы данных (например, SQLAlchemy)
    schema: type[SchemaType] = None  # Pydantic-схема, описывающая доменную модель

    @classmethod
    def map_to_domain_entity(cls, data):
        """
        Преобразует объект базы данных (например, SQLAlchemy-модель)
        в Pydantic-схему (доменную сущность).
        """
        return cls.schema.model_validate(data, from_attributes=True)

    @classmethod
    def map_to_persistence_entity(cls, data):
        """
        Преобразует Pydantic-схему в объект модели базы данных.
        """
        return cls.db_model(**data.model_dump())
