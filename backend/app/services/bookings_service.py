from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.bookings_repo import BookingRepo, BookingStatus
from ..repositories.payments_repo import PaymentRepo
from ..repositories.premises_repo import PremiseRepo
from ..repositories.users_repo import UserRepo
from ..schemas.bookings_scheme import BookingCreate
from ..schemas.payments_scheme import PaymentCreate
from ..services.payments_service import PaymentService


class BookingService:
    def __init__(self, db: AsyncSession):
        self.session = db
        # This session is used exclusively to maintain a single session throughout the entire booking creation function.
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

        Raises:
            HTTP_404 - In case the landlord or the premises do not exist.
            HTTP_409 - Foreign key, uniqueness, or date constraint violation.
            HTTP_403 - If user wants book his own premise
        """
        await self.check_coflicts_service(booking)
        # First, check for date conflicts and overlapping dates at the database level.

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
            if premise.landlord_id == renter_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You cannot book your own premise",
                )
            if premise.status == BookingStatus.CONFIRMED:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="You cannot book a space that has already been booked",
                )

            premise_price = await self.premise_session.get_premise_price_by_premise_id(
                booking.premise_id
            )

            total_price = PaymentService.calculator(
                premise_price, Range(booking.date_from, booking.date_to)
            )
            # This variable retrieves the total amount by calling a separate function that calculates the number of nights for the booking.

            await self.payment_session.balance_deduction(renter_id, total_price)
            # The user's balance is being deducted along with the total booking amount.

            payment_data = PaymentCreate(
                from_user_id=renter_id,
                to_landlord_id=landlord.id,
                for_premise_id=premise.id,
                total=total_price,
            )
            new_payment = await self.payment_session.create_payment(payment_data)
            # If an error occurs in the previous balance deduction function,
            # the payment creation function will not be called, and the transaction will be rolled back using `rollback()`.

            new_booking = await self.booking_session.create_booking(
                renter_id, booking, new_payment.id
            )
            # Finally, if the previous functions execute successfully,
            # the booking will be created and the ID of the newly created payment will be passed to it.

            await self.session.flush()
            await self.session.commit()
            return new_booking
        except IntegrityError as e:
            # If the database raises an integrity error inside the `try` block (foreign key, uniqueness, or our date constraint violation),
            # this block is executed. `e` stores information about the error.
            await self.session.rollback()
            if getattr(e.orig, "sqlstate", None) == "23P01":
                # `e.orig` is the original PostgreSQL driver error.
                # It has a `sqlstate` code. `23P01` means "exclusion constraint violation",
                # which indicates a violation of our date-overlap constraint.
                # `getattr(..., None)` safely returns `None` if the attribute does not exist, preventing the code from crashing.
                raise HTTPException(status_code=409, detail="Dates are already booked")
            raise
        except Exception:
            # Any other error (e.g., insufficient funds or a bug in the code) must also roll back the transaction.
            # It is then re-raised so that the upper level can handle it.
            await self.session.rollback()
            raise


    async def process_finished_bookings(self):
        