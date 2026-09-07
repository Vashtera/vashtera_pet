from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DisputeBase(BaseModel):
    id: int
    renter: str
    landlord: str
    booking: str
    status: str
    reason: str | None = Field(..., min_length=5, max_length=1000)
    moderator: str
    created_at: datetime


class DisputeCreate(BaseModel):
    renter: str
    landlord: str
    booking: str
    status: str
    reason: str | None = Field(..., min_length=5, max_length=1000)


class DisputeResponse(DisputeBase):
    model_config = ConfigDict(
        from_attributes=True,
    )
