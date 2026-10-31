from sqlalchemy import select
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.bookings_model import Booking
from ..schemas.bookings_scheme import BookingCreate


class BookingRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_conflict(self, booking: BookingCreate) -> Booking | None:
        """
        Checking for date overlap conflicts by premise_id

        Args:
            booking: the booking creation schema contains `premise_id`, `date_from`, and `date_to`

        Returns:
            Booking model or `None`
        """
        stmt = select(Booking).where(
            # Check by premise_id
            Booking.premise_id == booking.premise_id,
            # Check for date overlap conflicts
            Booking.during.overlaps(
                Range(booking.date_from, booking.date_to, bounds="[)")
            ),
        )
        conflicts = await self.session.execute(stmt)
        return conflicts.scalar_one_or_none()

    async def create_booking(
        self, renter_id: int, booking: BookingCreate
    ) -> Booking | None:
        """
        Creating a booking for an authenticated user

        Args:
            renter_id: is the ID of the user who wants to book the premises
            booking: the booking creation schema contains `premise_id`, `date_from`, and `date_to`

        Returns:
            Booking model or `None` if an exception occurs, the entire transaction will be rolled back
        """
        try:
            db_booking = Booking(
                premise_id=booking.premise_id,
                renter_id=renter_id,
                # Substitution into the booking date range
                during=Range(booking.date_from, booking.date_to),
            )
            self.session.add(db_booking)
            await self.session.flush()
            await self.session.refresh(db_booking)
            return db_booking
        except Exception:
            await self.session.rollback()
            raise
