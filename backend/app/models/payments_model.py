from datetime import UTC, datetime

from sqlalchemy import DECIMAL, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    # pending, received, rejected, frozen, paid
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)
    from_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )
    to_landlord_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )
    for_premise_id: Mapped[int] = mapped_column(
        ForeignKey("premises.id"), index=True, nullable=False
    )
    token: Mapped[str] = mapped_column(String(64), nullable=False)
    total: Mapped[float] = mapped_column(DECIMAL(2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
