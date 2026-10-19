from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.bookings_model import Booking


class BookingRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_booking(self, booking: Booking):
        try:
            self.session.add(Booking)
            await self.session.commit()
            await self.session.refresh(Booking)
            return booking
        except Exception:
            self.session.rollback()
            raise
