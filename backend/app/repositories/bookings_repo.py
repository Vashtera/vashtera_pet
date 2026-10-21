from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.bookings_model import Booking
from ..schemas.bookings_scheme import BookingCreate


class BookingRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_conflict(self, booking: BookingCreate) -> Booking | None:
        stmt = select(Booking).where(
            Booking.premise_id == booking.premise_id,
            Booking.during[2] > booking.date_from,
            Booking.during[1] < booking.date_to,
        )
        conflicts = await self.session.execute(stmt)
        return conflicts.scalar_one_or_none()

    async def create_booking(self, renter_id: int, booking: BookingCreate) -> Booking:
        db_booking = Booking(
            premise_id=booking.premise_id,
            renter_id=renter_id,
            date_from=booking.date_from,
            date_to=booking.date_to,
            # TODO TEMPORARY
            payment_id=3,
        )
        try:
            self.session.add(db_booking)
            await self.session.commit()
            await self.session.refresh(db_booking)
            return db_booking
        except Exception:
            await self.session.rollback()
            raise
