from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.payments_model import Payment


class PaymentRepo:
    def __init__(self, sessin: AsyncSession):
        self.session = self.session
