from datetime import UTC, datetime

from sqlalchemy import DECIMAL, TEXT, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Premise(Base):
    __tablename__ = "premises"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    type_id: Mapped[int] = mapped_column(
        ForeignKey("premise_type.id"),
        nullable=False,
        index=True,
    )
    type: Mapped["PremiseType"] = relationship(
        back_populates="premise",
        foreign_keys=[type_id],
    )
    landlord_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    landlord: Mapped["User"] = relationship(
        back_populates="user_premises",
        single_parent=True,
        foreign_keys=[landlord_id],
    )
    address_id: Mapped[int] = mapped_column(
        ForeignKey("premise_address.id"), index=True, nullable=False
    )
    address: Mapped["PremiseAddress"] = relationship(
        back_populates="premise",
        foreign_keys=[address_id],
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    views: Mapped[int] = mapped_column(default=0, nullable=False)
    description: Mapped[str | None] = mapped_column(TEXT)
    feature_id: Mapped[int] = mapped_column(
        ForeignKey("premise_feature.id"), index=True, nullable=False
    )
    feature: Mapped["PremiseFeature"] = relationship(
        back_populates="premise",
        foreign_keys=[feature_id],
    )
    # available, booked, archived, cancelled, pending
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
    premise: Mapped["Premise"] = relationship(back_populates="type")


class PremiseAddress(Base):
    __tablename__ = "premise_address"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    city: Mapped[str] = mapped_column(String(128), nullable=False)
    district: Mapped[str] = mapped_column(String(128), nullable=False)
    street: Mapped[str] = mapped_column(String(128), nullable=False)
    house_number: Mapped[str] = mapped_column(String(128), nullable=False)
    premise: Mapped["Premise"] = relationship(back_populates="address")


class PremiseFeature(Base):
    __tablename__ = "premise_feature"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    image: Mapped[str | None] = mapped_column(nullable=True)
    floor: Mapped[int | None] = mapped_column(nullable=True, default=1)
    rooms: Mapped[int | None] = mapped_column(nullable=True)
    area: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    premise: Mapped["Premise"] = relationship(back_populates="feature")
