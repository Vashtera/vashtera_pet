from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.payments_model import Payment
from ..models.users_model import User


class PaymentRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def balance_deduction(self, user_id: int, deduction_amount: Decimal):
        stmt = (
            update(User)
            .where(User.id == user_id, User.balance >= deduction_amount)
            .values(balance=User.balance - deduction_amount)
        )
        await self.session.execute(stmt)
        await self.session.flush()
