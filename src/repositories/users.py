# Импортируем EmailStr для валидации email'ов
from pydantic import EmailStr

from src.models.users import UsersOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import UserDataMapper
from src.schemas.users import UserWithHashedPassword

from sqlalchemy import select


class UsersRepository(BaseRepository):
    """
    Репозиторий для работы с пользователями. Используется для обращения к таблице users.

    Наследуется от BaseRepository и переопределяет:
    - модель ORM (UsersOrm)
    - маппер (UserDataMapper)
    """

    model = UsersOrm
    mapper = UserDataMapper

    async def get_user_with_hashed_password(self, email: EmailStr) -> UserWithHashedPassword:
        """
        Получение пользователя по email, включая хеш пароля.

        Этот метод используется при логине:
        - Ищем пользователя по email
        - Получаем ORM-объект
        - Преобразуем в схему `UserWithHashedPassword` (содержит email, id, hashed_password)

        :param email: Email пользователя (типизированный EmailStr)
        :raises sqlalchemy.exc.NoResultFound: если пользователь не найден
        :return: Pydantic-модель UserWithHashedPassword
        """
        # SELECT * FROM users WHERE email = :email
        query = select(self.model).filter_by(email=email)

        # Выполняем SQL-запрос
        result = await self.session.execute(query)

        # Получаем одну запись — ожидаем, что email уникальный
        model = result.scalars().one()

        # Конвертируем ORM → Pydantic с полем hashed_password
        return UserWithHashedPassword.model_validate(model)
