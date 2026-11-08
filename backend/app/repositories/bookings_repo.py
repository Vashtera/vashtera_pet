from datetime import date
from enum import StrEnum

from models.bookings_model import Booking
from schemas.bookings_scheme import BookingCreate
from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class BookingStatus(StrEnum):
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BookingRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_booking_by_id(self, booking_id: int) -> Booking | None:
        stmt = select(Booking).where(Booking.id == booking_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_booking_with_renter_by_id(
        self, booking_id: int, renter_id: int
    ) -> Booking | None:
        stmt = select(Booking).where(
            Booking.id == booking_id, Booking.renter_id == renter_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def check_conflict(self, booking: BookingCreate) -> Booking | None:
        """
        Checking for date overlap conflicts by premise_id

        Args:
            booking: the booking creation schema contains `premise_id`, `date_from`, and `date_to`

        Returns:
            Booking model or `None`
        """
        stmt = select(Booking).where(
            # Check for status
            Booking.status == BookingStatus.CONFIRMED,
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
        self,
        new_renter_id: int,
        booking: BookingCreate,
        new_payment_id: int,
    ) -> Booking | None:
        """
        Creating a booking for an authenticated user

        Args:
            renter_id: is the ID of the user who wants to book the premises
            booking: the booking creation schema contains `premise_id`, `date_from`, and `date_to`

        Returns:
            Booking model or `None` if an exception occurs, the entire transaction will be rolled back
        """
        db_booking = Booking(
            premise_id=booking.premise_id,
            renter_id=new_renter_id,
            # Substitution into the booking date range
            during=Range(booking.date_from, booking.date_to),
            payment_id=new_payment_id,
        )
        self.session.add(db_booking)
        await self.session.flush()
        await self.session.refresh(db_booking)
        return db_booking

    async def get_finished_booking_ids(self, today: date) -> list[int]:
        """Return IDs of confirmed bookings whose stay is already over.

        A booking is finished when its check-out date (the exclusive upper
        bound of ``during``) is on or before ``today``.

        Args:
            today: Current date used as the cutoff.

        Returns:
            IDs of bookings with status ``confirmed`` that are ready to be
            completed and paid out.
        """
        stmt = select(Booking.id).where(
            Booking.status == BookingStatus.CONFIRMED,
            func.upper(Booking.during) <= today,
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_status_to_completed(self, booking_id: int) -> None:
        """Set the booking status to ``completed``.

        Flushes the change but does not commit; the caller owns the transaction.

        Args:
            booking_id: ID of the booking to update.
        """
        stmt = (
            update(Booking)
            .where(Booking.id == booking_id)
            .values(status=BookingStatus.COMPLETED)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def update_status_to_cancelled(self, booking_id: int) -> None:
        """Set the booking status to ``cancelled``.

        Flushes the change but does not commit; the caller owns the transaction.
        A cancelled booking no longer blocks its dates.

        Args:
            booking_id: ID of the booking to update.
        """
        stmt = (
            update(Booking)
            .where(Booking.id == booking_id)
            .values(status=BookingStatus.CANCELLED)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_arrival_date_by_id(self, booking_id: int) -> date | None:
        """Return the check-in date of a confirmed booking.

        Args:
            booking_id: ID of the booking.

        Returns:
            The lower bound of ``during``, or None if the booking does not
            exist or is not in ``confirmed`` status.
        """
        stmt = select(func.lower(Booking.during)).where(
            Booking.id == booking_id, Booking.status == BookingStatus.CONFIRMED
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
