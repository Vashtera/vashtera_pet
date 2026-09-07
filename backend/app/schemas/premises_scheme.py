from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PremiseBase(BaseModel):
    type: str
    landlord: str
    address: str
    created_at: datetime
    views: int
    description: str | None = Field(..., min_length=5, max_length=1000)
    feature: str
    status: str


class PremiseCreate(PremiseBase): ...


class PremisePublic(PremiseBase):
    model_config = ConfigDict(
        from_attributes=True,
    )


class PremisePrivate(PremiseBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class PremiseUpdate(BaseModel):
    description: str | None = Field(..., min_length=5, max_length=1000)
    feature: str
