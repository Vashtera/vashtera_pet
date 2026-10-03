from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AddressResponse(ORMBase):
    street: str
    city: str
    district: str


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
    floor: int
    area: float
    rooms: int
    price: int


class PremiseResponse(ORMBase):
    views: int
    contact_number: str
    created_at: datetime
    description: str
    status: str
    address: AddressResponse
    landlord: LandlordResponse
    type: TypeResponse
    feature: FeatureResponse


class PaginatedPremisesResponse(ORMBase):
    premises: list[PremiseResponse]
