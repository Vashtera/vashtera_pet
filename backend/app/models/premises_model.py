from datetime import UTC, datetime

from core.config import settings
from database import Base
from sqlalchemy import DECIMAL, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

PREMISE_TYPES = {
    1: "apartments",
    2: "house",
    3: "country_house",
    4: "commercial_premise",
    5: "warehouse",
}


class Premise(Base):
    __tablename__ = "premises"
