from fastapi import APIRouter, Depends, status

from ..auth import CurrentUser
from ..database import get_db
from ..schemas.bookings_scheme import BookingCreate, BookingResponse
from ..services.bookings_service import BookingService

router = APIRouter()


def get_booking_service(session=Depends(get_db)):
    return BookingService(session)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_booking(
    renter: CurrentUser,
    booking: BookingCreate,
    db: BookingService = Depends(get_booking_service),
):
    return await db.create_booking(renter.id, booking)
