from datetime import UTC, datetime
from decimal import Decimal

from database import Base
from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import CheckConstraint


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    # "frozen", "released", "refunded"
    status: Mapped[str] = mapped_column(String, default="frozen", nullable=False)
    from_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )
    from_user: Mapped["User"] = relationship(
        "User", foreign_keys="Payment.from_user_id"
    )
    to_landlord_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )
    to_landlord: Mapped["User"] = relationship(
        "User", foreign_keys="Payment.to_landlord_id"
    )
    for_premise_id: Mapped[int] = mapped_column(
        ForeignKey("premises.id"), index=True, nullable=False
    )
    for_premise: Mapped["Premise"] = relationship(
        "Premise", foreign_keys="Payment.for_premise_id"
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        CheckConstraint("total >= 0", name="check_total"),
        default=Decimal("0"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
