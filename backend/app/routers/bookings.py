from fastapi import APIRouter, Depends, status

from ..database import get_db
from ..schemas.bookings_scheme import BookingCreate, BookingResponse
from ..services.bookings_service import BookingService

router = APIRouter()


def get_booking_service(session=Depends(get_db)):
    return BookingService(session)
