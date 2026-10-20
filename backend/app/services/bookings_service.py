from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.bookings_repo import BookingRepo
from ..schemas.bookings_scheme import BookingCreate


class BookingService:
    def __init__(self, db: AsyncSession):
        self.session = BookingRepo(db)

    async def check_coflicts_service(self, booking: BookingCreate):
        conflicts = await self.session.check_conflict(booking)
        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The selected time range is conflicts with an existing bookings for this time",
            )

    async def create_booking(self, renter_id: int, booking: BookingCreate):
        await self.check_coflicts_service(booking)
        return await self.session.create_booking(renter_id, booking)
