class BaseClassException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(BaseClassException):
    detail = "Обьект не найден"


class AllRoomsAreBookedException(BaseClassException):
    detail = "Не осталось свободных номеров"

class UserAlreadyExistsException(BaseClassException):
    detail = "Пользователь уже существует"

class InvalidDateRangeException(BaseClassException):
    detail = "Дата выезда не может быть раньше даты заезда"

class NoHotelsFoundException(BaseClassException):
    detail = "Подходящие отели не найдены"

class NoRoomsFoundException(BaseClassException):
    detail = "Свободные номера не найдены"

