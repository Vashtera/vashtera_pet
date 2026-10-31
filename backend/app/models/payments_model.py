from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    # pending, received, rejected, frozen, paid
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)
    from_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )
    from_user: Mapped["User"] = relationship("User", foreign_keys="from_user_id")
    to_landlord_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )
    to_landlord: Mapped["User"] = relationship("User", foreign_keys="from_user_id")
    for_premise_id: Mapped[int] = mapped_column(
        ForeignKey("premises.id"), index=True, nullable=False
    )
    for_premise: Mapped["Premise"] = relationship(
        "Premise", foreign_keys="from_user_id"
    )
    token: Mapped[str] = mapped_column(String(64), nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
