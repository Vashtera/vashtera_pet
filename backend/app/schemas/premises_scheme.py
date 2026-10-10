from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ShortAddressResponse(ORMBase):
    street: str
    city: str
    district: str


class FullAddressResponse(ShortAddressResponse):
    house_number: int | None


class LandlordResponse(ORMBase):
    id: int
    username: str
    image_file: str | None = None


class FeatureResponse(ORMBase):
    image: str | None = None
    floor: int | None
    area: float
    rooms: int
    price: int


class PremiseResponse(ORMBase):
    views: int
    contact_number: str
    created_at: datetime
    description: str | None
    status: str
    address: FullAddressResponse
    landlord: LandlordResponse
    premise_type: str
    feature: FeatureResponse


class ShortPremiseResponse(ORMBase):
    id: int
    views: int
    created_at: datetime
    premise_type: str
    feature: FeatureResponse
    address: ShortAddressResponse


class PremiseCreate(ORMBase):
    premise_type: Literal[
        "apartments", "house", "country_house", "commercial", "warehouse"
    ]
    description: str | None
    contact_number: str


class PremiseUpdate(ORMBase):
    contact_number: str | None
    description: str | None
    address: FullAddressResponse | None
    premise_type: str | None
    feature: FeatureResponse | None
