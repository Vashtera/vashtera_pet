from datetime import date, datetime

from fastapi import HTTPException, status
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.bookings_repo import BookingRepo
from ..repositories.payments_repo import PaymentRepo
from ..repositories.premises_repo import PremiseRepo
from ..repositories.users_repo import UserRepo
from ..schemas.bookings_scheme import BookingCreate
from ..schemas.payments_scheme import PaymentCreate
from ..services.payments_service import PaymentService


class BookingService:
    def __init__(self, db: AsyncSession):
        self.session = db
        self.booking_session = BookingRepo(db)
        self.payment_session = PaymentRepo(db)
        self.premise_session = PremiseRepo(db)
        self.user_session = UserRepo(db)

    async def check_coflicts_service(self, booking: BookingCreate) -> None:
        """
        Function for checking conflicts and protecting against incorrect date input.

        Args:
            booking - Schema for creating a booking that contains the premise ID, check-in date, and check-out date.
        """
        if booking.date_from == booking.date_to:
            # Validation to prevent the check-out date from being equal to the check-in date and avoid database-level errors.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The check-in and check-out dates cannot be the same.",
            )
        if booking.date_from < date.today():
            # Validation to prevent creating a booking for dates in the past.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot enter a date from the past.",
            )
        conflicts = await self.booking_session.check_conflict(booking)
        # A variable that calls the repository to check for conflicts at the database level and prevent date overlaps.
        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The selected time range is conflicts with an existing bookings for this time",
            )

    async def create_booking(self, renter_id: int, booking: BookingCreate):
        """
        Function for creating a booking for a registered user.

        Args:
            renter_id - ID of the registered user who creates the booking.
            booking - Schema for creating a booking that contains the premise ID, check-in date, and check-out date.

        Returns:
            A new booking with an associated payment created for it and the booking marked as paid.

        Exceptions:
            HTTP_404 -
        """
        await self.check_coflicts_service(booking)

        try:
            landlord = await self.premise_session.get_premise_landlord(
                booking.premise_id
            )
            if landlord is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Landlord not found"
                )
            premise = await self.premise_session.get_premise_by_id(booking.premise_id)
            if premise is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Premise not found"
                )

            premise_price = await self.premise_session.get_premise_price_by_premise_id(
                booking.premise_id
            )

            total_price = PaymentService.calculator(
                premise_price, Range(booking.date_from, booking.date_to)
            )

            await self.payment_session.balance_deduction(renter_id, total_price)

            payment_data = PaymentCreate(
                from_user_id=renter_id,
                to_landlord_id=landlord.id,
                for_premise_id=premise.id,
                total=total_price,
            )
            new_payment = await self.payment_session.create_payment(payment_data)

            new_booking = await self.booking_session.create_booking(
                renter_id, booking, new_payment.id
            )

            await self.session.flush()
            await self.session.commit()
            return new_booking
        except IntegrityError as e:
            await self.session.rollback()
            if getattr(e.orig, "sqlstate", None) == "23P01":
                raise HTTPException(status_code=409, detail="Dates are already booked")
            raise
        except Exception:
            await self.session.rollback()
            raise
