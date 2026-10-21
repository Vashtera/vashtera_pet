from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import TSRANGE, ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    premise_id: Mapped[int] = mapped_column(
        ForeignKey("premises.id"), index=True, nullable=False
    )
    renter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )
    during: Mapped[TSRANGE] = mapped_column(TSRANGE, nullable=False)
    # "pending", "approve", "reject"
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="pending")
    payment_id: Mapped[int] = mapped_column(
        ForeignKey("payments.id"), index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    __table_args__ = (ExcludeConstraint(("premise_id", "="), ("during", "&&")),)
