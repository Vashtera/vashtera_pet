from datetime import UTC, datetime

from core.config import settings
from database import Base
from sqlalchemy import DECIMAL, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Premise(Base):
    __tablename__ = "premises"
