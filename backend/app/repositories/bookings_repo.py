from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.bookings_model import Booking


class BookingRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
