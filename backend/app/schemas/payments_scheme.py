from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from ..schemas.premises_scheme import PremiseResponse
from ..schemas.users_scheme import UserPrivate, UserPublic


class PaymentBase(BaseModel):
    id: int
    from_user: UserPublic
    to_landlord: UserPrivate
    for_premise: PremiseResponse
    total: Decimal


class PaymentCreate(BaseModel):
    from_user_id: int
    to_landlord_id: int
    for_premise_id: int
    total: Decimal

    model_config = ConfigDict(
        from_attributes=True,
    )


class PaymentResponse(PaymentBase):
    model_config = ConfigDict(
        from_attributes=True,
    )
