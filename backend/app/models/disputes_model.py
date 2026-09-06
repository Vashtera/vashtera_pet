from datetime import UTC, datetime

from app.database import Base
from sqlalchemy import DECIMAL, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Dispute(Base):
    __tablename__ = "disputes"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    renter_id: Mapped[int] = relationship(back_populates="users.id")
    landlord_id: Mapped[int] = relationship(back_populates="users.id")
    booking_id: Mapped[int] = relationship(back_populates="bookings.id")
    mod_dispute: Mapped[int] = relationship(back_populates="users.id")
    # under_review, two_party_dispute_resolution, three_party_dispute_resolution, completed
    status: Mapped[str] = mapped_column(
        String(64), nullable=False, default="under_review"
    )
    decision: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
