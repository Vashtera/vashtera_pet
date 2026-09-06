from datetime import UTC, datetime

from app.database import Base
from sqlalchemy import DECIMAL, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Dispute(Base):
    __tablename__ = "disputes"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
