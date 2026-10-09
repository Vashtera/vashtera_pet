from fastapi import APIRouter, Depends, status

from ..auth import CurrentUser
from ..database import get_db
from ..schemas.premises_scheme import (
    FeatureResponse,
    FullAddressResponse,
    PremiseCreate,
    PremiseResponse,
    ShortPremiseResponse,
)
from ..services.premises_service import PremiseService

router = APIRouter()


def get_premise_service(session=Depends(get_db)):
    return PremiseService(session)


@router.get(
    "/{premise_id}", response_model=PremiseResponse, status_code=status.HTTP_200_OK
)
async def get_premise_by_id(
    premise_id: int, db: PremiseService = Depends(get_premise_service)
):
    return await db.get_premise_by_id(premise_id)


@router.get(
    "/city/{premise_city}",
    response_model=list[ShortPremiseResponse],
    status_code=status.HTTP_200_OK,
)
async def get_premises_by_city(
    premise_city: str, db: PremiseService = Depends(get_premise_service)
):
    return await db.get_premises_by_city(premise_city)


@router.post(
    "/new", response_model=PremiseResponse, status_code=status.HTTP_201_CREATED
)
async def create_premise(
    address: FullAddressResponse,
    features: FeatureResponse,
    premise_data: PremiseCreate,
    current_user: CurrentUser,
    db: PremiseService = Depends(get_premise_service),
):
    return await db.create_premise(address, features, current_user.id, premise_data)
