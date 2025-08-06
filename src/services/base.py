from src.utils.db_manager import DBManager


class BaseService:
    """
    Базовый сервис, предоставляющий доступ к менеджеру базы данных (DBManager).
    От него наследуются все остальные сервисы, которым нужен доступ к БД.
    """

    db: DBManager  # Менеджер для работы с базой данных

    def __init__(self, db: DBManager | None = None) -> None:
        """
        Инициализация базового сервиса с переданным DBManager.

        :param db: экземпляр DBManager (если None — должен быть установлен вручную)
        """
        self.db = db
