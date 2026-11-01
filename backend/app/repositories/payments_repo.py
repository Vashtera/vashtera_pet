from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.payments_model import Payment
from ..models.users_model import User
from ..schemas.payments_scheme import PaymentCreate


class PaymentRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_payment_by_id(self, payment_id: int) -> Payment | None:
        """
        Retrieve a payment by ID.

        Args:
            payment_id - ID of the payment to be retrieved.

        Returns:
            Payment or None
        """
        stmt = select(Payment).where(Payment.id == payment_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def balance_deduction(self, user_id: int, deduction_amount: Decimal) -> None:
        """
        Function for deducting a user's balance by their ID,
        ensuring that the balance is greater than or equal to the deduction amount.

        Args:
            user_id - The ID of the user whose balance needs to be deducted.
            deduction_amount - The total amount to be deducted in decimal format.
        """
        stmt = (
            update(User)
            .where(User.id == user_id, User.balance >= deduction_amount)
            .values(balance=User.balance - deduction_amount)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def create_payment(self, payment_data: PaymentCreate) -> Payment:
        """
        Payment creation function.

        Args:
            payment_data - Schema for creating a payment containing the user ID, landlord ID, premise ID, and total payment amount.

        Returns:
            The newly created payment model.
        """
        new_payment = Payment(**payment_data.model_dump())
        self.session.add(new_payment)
        await self.session.flush()
        return new_payment
