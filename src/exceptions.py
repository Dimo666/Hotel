from datetime import date
from fastapi import HTTPException


class BaseClassException(Exception):
    """
    Базовое исключение для пользовательских ошибок приложения.
    """
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(BaseClassException):
    """
    Исключение, если объект не найден.
    """
    detail = "Обьект не найден"


class ObjectAlreadyExistsException(BaseClassException):
    """
    Исключение, если объект уже существует.
    """
    detail = "Похожий обьект уже существует"


class AllRoomsAreBookedException(BaseClassException):
    """
    Исключение, если все номера уже забронированы.
    """
    detail = "Не осталось свободных номеров"


class UserAlreadyExistsException(BaseClassException):
    """
    Исключение, если пользователь уже существует.
    """
    detail = "Пользователь уже существует"


def check_dete_to_after_date_from(date_from: date, date_to: date) -> None:
    """
    Проверяет, что дата выезда позже даты заезда.

    :param date_from: Дата заезда
    :param date_to: Дата выезда
    :raises HTTPException: Если дата выезда раньше или равна дате заезда
    """
    if date_to <= date_from:
        raise HTTPException(status_code=422, detail="Дата заезда не может быть позже даты выезда")


class BaseClassHTTPException(HTTPException):
    """
    Базовый класс HTTP-исключений с предустановленным статусом и сообщением.
    """
    status_code = 500
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class HotelNotFoundException(BaseClassHTTPException):
    """
    HTTP-исключение, если отель не найден.
    """
    status_code = 404
    detail = "Отель не найден"


class RoomNotFoundException(BaseClassHTTPException):
    """
    HTTP-исключение, если номер не найден.
    """
    status_code = 404
    detail = "Номер не найден"





