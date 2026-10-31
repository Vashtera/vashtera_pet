from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.payments_repo import PaymentRepo


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.session = PaymentRepo(db)

    def calculator(self, premise_price: Decimal, during: Range) -> Decimal:
        date_from = during.lower
        date_to = during.upper
        if date_from is None or date_to is None:
            raise ValueError(
                "during must have both lower and upper bounds",
            )
        nights = (date_to - date_from).days
        return premise_price * nights
