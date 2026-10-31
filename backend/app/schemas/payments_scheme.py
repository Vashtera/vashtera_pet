from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from ..schemas.premises_scheme import PremiseResponse
from ..schemas.users_scheme import UserPrivate, UserPublic


class PaymentBase(BaseModel):
    id: int
    from_user: UserPrivate
    to_landlord: UserPublic
    for_premise: PremiseResponse
    total: Decimal
    created_at: datetime


class PaymentCreate(BaseModel):
    from_user: UserPrivate
    to_landlord: UserPublic
    for_premise: PremiseResponse
    total: Decimal
    created_at: datetime


class PaymentResponse(PaymentBase):
    model_config = ConfigDict(
        from_attributes=True,
    )
