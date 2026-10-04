from datetime import datetime

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


class TypeResponse(ORMBase):
    is_countryHouse: bool
    is_warehouse: bool
    is_house: bool
    is_apartments: bool
    is_commercialPremise: bool


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
    type: TypeResponse
    feature: FeatureResponse


class ShortPremiseResponse(ORMBase):
    id: int
    views: int
    created_at: datetime
    type: TypeResponse
    feature: FeatureResponse
    address: ShortAddressResponse


class PremiseCreate(ORMBase):
    type: TypeResponse
    address: FullAddressResponse
    feature: FeatureResponse
    description: str | None
    contact_number: str
