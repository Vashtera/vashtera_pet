from fastapi import APIRouter, Depends, status

from ..auth import CurrentUser
from ..database import get_db
from ..schemas.bookings_scheme import BookingCreate, BookingResponse
from ..services.bookings_service import BookingService

router = APIRouter()


def get_booking_service(session=Depends(get_db)):
    """Provides a `BookingService` instance as a FastAPI dependency.

    Args:
        session: Database session injected via the `get_db` dependency.

    Returns:
        BookingService: Service wrapping the given database session.
    """
    return BookingService(session)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_booking(
    renter: CurrentUser,
    booking: BookingCreate,
    db: BookingService = Depends(get_booking_service),
):
    """Creates a new booking for the current user.

    The authenticated user is recorded as the renter of the booking.

    Args:
        renter (CurrentUser): Authenticated user making the booking.
        booking (BookingCreate): Booking details (request body).
        db (BookingService): Booking service injected via dependency.

    Returns:
        The newly created booking (HTTP 201).
    """
    return await db.create_booking(renter.id, booking)
