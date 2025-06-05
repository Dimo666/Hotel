from src.models.bookings import BookingsOrm
from src.repositories.base import BaseRepository
from src.schemas.bookings import BookingsCreate, BookingsRead


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    schema = BookingsRead

