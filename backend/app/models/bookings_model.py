from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    premise_id: Mapped[int] = relationship(
        back_populates="premises.id", cascade="all, delete-orphan"
    )
    renter_id: Mapped[int] = relationship(
        back_populates="users.id", cascade="all, delete-orphan"
    )
    landlord_id: Mapped[int] = relationship(
        back_populates="premises.id", cascade="all, delete-orphan"
    )
    date_from: Mapped[datetime] = mapped_column(DateTime)
    date_to: Mapped[datetime] = mapped_column(DateTime)
    # "pending", "approve", "reject"
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="pending")
    payment_id: Mapped[int] = relationship(back_populates="payments.id")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
