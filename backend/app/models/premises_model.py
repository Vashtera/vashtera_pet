from datetime import UTC, datetime

from sqlalchemy import DECIMAL, TEXT, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class Premise(Base):
    __tablename__ = "premises"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    type_id: Mapped[int] = relationship(
        back_populates="premise_type.id", cascade="all, delete-orphan"
    )
    landlord_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    address_id: Mapped[int] = relationship(
        back_populates="premise_address.id", cascade="all, delete-orphan"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    views: Mapped[int] = mapped_column(default=0, nullable=False)
    description: Mapped[str | None] = mapped_column(TEXT)
    feature_id: Mapped[int] = relationship(
        back_populates="premise_feature.id",
        cascade="all, delete-orphan",
    )
    # available, booked, archived, cancelled, "archived"
    status: Mapped[str] = mapped_column(String, default="pending")
    contact_number: Mapped[str] = mapped_column(String(12), nullable=False)


class PremiseType(Base):
    __tablename__ = "premise_type"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    is_apartments: Mapped[bool] = mapped_column(default=False)
    is_house: Mapped[bool] = mapped_column(default=False)
    is_countryHouse: Mapped[bool] = mapped_column(default=False)
    is_commercialPremise: Mapped[bool] = mapped_column(default=False)
    is_warehouse: Mapped[bool] = mapped_column(default=False)


class PremiseAddress(Base):
    __tablename__ = "premise_address"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    city: Mapped[str] = mapped_column(String(128), nullable=False)
    district: Mapped[str] = mapped_column(String(128), nullable=False)
    street: Mapped[str] = mapped_column(String(128), nullable=False)
    house_number: Mapped[str] = mapped_column(String(128), nullable=False)


class PremiseFeature(Base):
    __tablename__ = "premise_feature"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    image: Mapped[str | None] = mapped_column(nullable=True)
    floor: Mapped[int | None] = mapped_column(nullable=True, default=1)
    rooms: Mapped[int | None] = mapped_column(nullable=True)
    area: Mapped[float] = mapped_column(DECIMAL(1), nullable=False)
    price: Mapped[float] = mapped_column(DECIMAL(2), nullable=False)
