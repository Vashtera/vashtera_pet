from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BookingBase(BaseModel):
    id: int
    premise: str
    renter: str
    landlord: str
    date_from: datetime
    date_to: datetime
    status: str
    payment: str
    created_at: datetime


class BookingCreate(BaseModel):
    premise: str
    renter: str
    landlord: str
    date_from: datetime
    date_to: datetime
    status: str
    payment: str


class BookingResponse(BookingBase):
    model_config = ConfigDict(
        from_attributes=True,
    )


class BookingUpdate(BaseModel):
    status: str
    date_from: datetime
    date_to: datetime
