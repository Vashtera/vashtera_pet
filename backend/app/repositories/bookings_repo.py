from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.bookings_model import Booking
from ..schemas.bookings_scheme import BookingCreate


class BookingRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_conflict(self, booking: BookingCreate):
        stmt = select(Booking).where(
            Booking.premise_id == booking.premise_id,
            Booking.date_to < booking.date_from,
            Booking.date_from > booking.date_to,
        )
        conflicts = await self.session.execute(stmt)
        return conflicts.scalar_one_or_none()

    async def create_booking(self, booking: Booking):
        try:
            self.session.add(Booking)
            await self.session.commit()
            await self.session.refresh(Booking)
            return booking
        except Exception:
            await self.session.rollback()
            raise
