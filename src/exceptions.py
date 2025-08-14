from datetime import date
from fastapi import HTTPException


class BaseClassException(Exception):
    """
    Базовое исключение для бизнес-ошибок приложения (не HTTP).
    Все кастомные ошибки должны наследоваться от него.
    """

    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(BaseClassException):
    """
    Исключение, если любой объект не найден (универсальное).
    """

    detail = "Объект не найден"


class RoomNotFoundException(BaseClassException):
    """
    Исключение, если номер (комната) не найден.
    """

    detail = "Номер не найден"


class HotelNotFoundException(BaseClassException):
    """
    Исключение, если отель не найден.
    """

    detail = "Отель не найден"


class ObjectAlreadyExistsException(BaseClassException):
    """
    Исключение, если объект уже существует.
    """

    detail = "Похожий объект уже существует"


class AllRoomsAreBookedException(BaseClassException):
    """
    Исключение, если все номера в отеле уже забронированы в заданный период.
    """

    detail = "Не осталось свободных номеров"


class IncorrectTokenException(BaseClassException):
    detail = "Некорректный токен"


class EmailNotRegisteredException(BaseClassException):
    detail = "Пользователь с таким email не зарегистрирован"


class IncorrectPasswordException(BaseClassException):
    detail = "Пароль неверный"


class UserAlreadyExistsException(BaseClassException):
    """
    Исключение, если пользователь с таким email уже существует.
    """

    detail = "Пользователь уже существует"


def check_date_to_after_date_from(date_from: date, date_to: date) -> None:
    """
    Проверка, что дата выезда позже даты заезда.

    :param date_from: Дата заезда
    :param date_to: Дата выезда
    :raises HTTPException: если date_to раньше или равна date_from
    """
    if date_to <= date_from:
        raise HTTPException(status_code=422, detail="Дата заезда не может быть позже даты выезда")


class BaseClassHTTPException(HTTPException):
    """
    Базовый класс для HTTP-исключений с предустановленным статусом и detail-сообщением.
    Удобен для использования с FastAPI.
    """

    status_code = 500
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class HotelNotFoundHTTPException(BaseClassHTTPException):
    """
    HTTP-ошибка 404, если отель не найден.
    """

    status_code = 404
    detail = "Отель не найден"


class RoomNotFoundHTTPException(BaseClassHTTPException):
    """
    HTTP-ошибка 404, если номер не найден.
    """

    status_code = 404
    detail = "Номер не найден"


class AllRoomsAreBookedHTTPException(BaseClassHTTPException):
    status_code = 409
    detail = "Не осталось свободных номеров"


class IncorrectTokenHTTPException(BaseClassHTTPException):
    detail = "Некорректный токен"


class EmailNotRegisteredHTTPException(BaseClassHTTPException):
    status_code = 401
    detail = "Пользователь с таким email не зарегистрирован"


class UserEmailAlreadyExistsHTTPException(BaseClassHTTPException):
    status_code = 409
    detail = "Пользователь с такой почтой уже существует"


class IncorrectPasswordHTTPException(BaseClassHTTPException):
    status_code = 401
    detail = "Пароль неверный"


class NoAccessTokenHTTPException(BaseClassHTTPException):
    status_code = 401
    detail = "Вы не предоставили токен доступа"
