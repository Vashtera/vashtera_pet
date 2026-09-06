from datetime import UTC, datetime

from core.config import settings
from database import Base
from sqlalchemy import DECIMAL, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(
        String(128), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    image_file: Mapped[str] = mapped_column(String(200))
    reset_tokens: Mapped[int] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # TEMPORARY
    favorite_premises: Mapped[int] = ...
    balance: Mapped[float] = mapped_column(DECIMAL(2), default=0)
    role_id: Mapped[int] = relationship(
        back_populates="roles.id",
        cascade="all, delete-orphan",
    )

    # TEMPORARY
    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"https://{settings.s3_bucket_name}.s3.{settings.s3_region}.amazonaws.com/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    user: Mapped[User] = relationship(
        back_populates="reset_tokens",
        cascade="all, delete-orphan",
    )


class Roles(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    is_landLord: Mapped[bool] = mapped_column(default=False)
    is_modDisputes: Mapped[bool] = mapped_column(default=False)
    is_modListings: Mapped[bool] = mapped_column(default=False)
    is_superMod: Mapped[bool] = mapped_column(default=False)
