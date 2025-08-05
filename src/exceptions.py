class BaseClassException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(BaseClassException):
    detail = "Обьект не найден"


class AllRoomsAreBookedException(BaseClassException):
    detail = "Не осталось свободных номеров"
