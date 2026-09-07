from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PaymentBase(BaseModel):
    id: int
    from_user: str
    to_landlord: str
    for_premise: str
    total: float
    created_at: datetime


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    model_config = ConfigDict(
        from_attributes=True,
    )
