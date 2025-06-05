from pydantic import BaseModel, conint, ConfigDict

from datetime import date

class BookingsCreate(BaseModel):
    date_from: date
    date_to: date
    room_id: conint(gt=0)

class BookingsRead(BaseModel):
    id: int
    user_id: int
    room_id: int
    date_from: date
    date_to: date
    price: int
    total_cost: int

    model_config = ConfigDict(from_attributes=True)


class BookingsDBCreate(BookingsCreate):
    user_id: int
    price: int
