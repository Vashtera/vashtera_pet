from datetime import UTC, datetime

from app.database import Base
from sqlalchemy import DECIMAL, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    # pending, received, rejected, frozen, paid
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)
    from_user: Mapped[id] = relationship(
        back_populates="users.id",
        cascade="all, delete-orphan",
    )
    to_landlord: Mapped[id] = relationship(
        back_populates="users.id",
        cascade="all, delete-orphan",
    )
    for_premise: Mapped[int] = relationship(
        back_populates="premises.id",
        cascade="all, delete-orphan",
    )
    token: Mapped[str] = mapped_column(String(64), nullable=False)
    total: Mapped[float] = mapped_column(DECIMAL(2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
