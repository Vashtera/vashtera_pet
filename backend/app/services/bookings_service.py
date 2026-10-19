from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.bookings_repo import BookingRepo
from ..schemas.bookings_scheme import BookingCreate


class BookingService:
    def __init__(self, db: AsyncSession):
        self.session = BookingRepo(db)

    async def create_booking(self, booking: BookingCreate): ...
