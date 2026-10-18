from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ..schemas.premises_scheme import ShortPremiseResponse
from ..schemas.users_scheme import UserPublic


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BookingCreate(ORMBase):
    premise: str
    renter: str
    date_from: datetime
    date_to: datetime


class BookingResponse(ORMBase):
    id: int
    premise: ShortPremiseResponse
    landlord: UserPublic
    date_from: datetime
    date_to: datetime
    status: str
    payment: str
    created_at: datetime


class BookingUpdate(ORMBase):
    date_from: datetime | None
    date_to: datetime | None
