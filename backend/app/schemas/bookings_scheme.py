from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from ..schemas.premises_scheme import ShortPremiseResponse
from ..schemas.users_scheme import UserPublic


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BookingCreate(ORMBase):
    premise_id: int
    date_from: datetime
    date_to: datetime


class BookingResponse(ORMBase):
    id: int
    premise: ShortPremiseResponse
    landlord: UserPublic
    date_from: datetime
    date_to: datetime
    status: Literal["pending", "approve", "reject"]
    payment: str
    created_at: datetime


class BookingUpdate(ORMBase):
    date_from: datetime | None
    date_to: datetime | None
