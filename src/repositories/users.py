# Импортируем EmailStr для валидации email'ов
from pydantic import EmailStr

# Импортируем ORM-модель пользователя
from src.models.users import UsersOrm

# Импортируем базовый репозиторий с общими методами для работы с БД
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import UserDataMapper

# Импортируем схемы пользователя
from src.schemas.users import UserWithHashedPassword

# Импортируем функцию для составления SQL-запросов
from sqlalchemy import select


# Репозиторий для работы с пользователями, наследуется от общего BaseRepository
class UsersRepository(BaseRepository):
    # Указываем, с какой моделью БД работает этот репозиторий
    model = UsersOrm
    # И с какой схемой он работает на уровне Python-объектов
    mapper = UserDataMapper

    # Метод для получения пользователя по email с хешированным паролем
    async def get_user_with_hashed_password(self, email: EmailStr):
        # Создаём запрос: выбираем пользователя, у которого email совпадает
        query = select(self.model).filter_by(email=email)

        # Выполняем запрос в асинхронной сессии
        result = await self.session.execute(query)

        # Получаем одну запись (ожидаем, что email уникальный и вернётся ровно один пользователь)
        model = result.scalars().one()

        # Валидируем ORM-объект в Pydantic-схему UserWithHashedPassword
        return UserWithHashedPassword.model_validate(model)
