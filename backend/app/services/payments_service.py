from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException, status
from repositories.payments_repo import PaymentRepo
from services.bookings_service import COMMISSION_RATE
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.ext.asyncio import AsyncSession


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.session = PaymentRepo(db)

    @staticmethod
    def calculator(premise_price: Decimal, during: Range) -> Decimal:
        """Calculates the total price of a stay.

        Multiplies the per-night premise price by the number of nights in the
        given date range. The number of nights is the difference in days
        between the upper and lower bounds of the range.

        Args:
            premise_price (Decimal): Price of the premise per night.
            during (Range): Date range of the stay, with both a lower bound
                (check-in) and an upper bound (check-out).

        Returns:
            Decimal: Total cost of the stay (`premise_price` multiplied by
                the number of nights).

        Raises:
            ValueError: If `during` is missing its lower or upper bound.
        """
        date_from = during.lower
        date_to = during.upper
        if date_from is None or date_to is None:
            raise ValueError(
                "during must have both lower and upper bounds",
            )
        nights = (date_to - date_from).days
        return premise_price * nights

    @staticmethod
    def commission_calculation(
        amount: Decimal,
    ) -> Decimal:
        """Calculate the platform commission for a payment amount.

        The commission is ``amount * COMMISSION_RATE``, rounded to cents using
        ROUND_HALF_UP.

        Args:
            amount: Total payment amount.

        Returns:
            The commission, quantized to two decimal places.
        """
        commission = (amount * COMMISSION_RATE).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
            # This is a rounding rule. "Half up" is the standard method taught in school:
            # if the next digit is 5 or greater, round up. Otherwise, round down.
        )
        return commission
