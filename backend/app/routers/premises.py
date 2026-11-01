from fastapi import APIRouter, Depends, status

from ..auth import CurrentUser
from ..database import get_db
from ..schemas.premises_scheme import (
    AddressCreate,
    FeatureCreate,
    PremiseCreate,
    PremiseResponse,
    PremiseUpdate,
    ShortPremiseResponse,
)
from ..services.premises_service import PremiseService

router = APIRouter()


def get_premise_service(session=Depends(get_db)):
    """Provides a `PremiseService` instance as a FastAPI dependency.

    Args:
        session: Database session injected via the `get_db` dependency.

    Returns:
        PremiseService: Service wrapping the given database session.
    """
    return PremiseService(session)


@router.get(
    "", response_model=list[ShortPremiseResponse], status_code=status.HTTP_200_OK
)
async def get_all_premises(db: PremiseService = Depends(get_premise_service)):
    """Returns all premises.

    Args:
        db (PremiseService): Premise service injected via dependency.

    Returns:
        list[ShortPremiseResponse]: Short representations of all premises.
    """
    return await db.get_all_premises()


@router.get(
    "/{premise_id}", response_model=PremiseResponse, status_code=status.HTTP_200_OK
)
async def get_premise_by_id(
    premise_id: int, db: PremiseService = Depends(get_premise_service)
):
    """Returns a single premise by its identifier.

    Args:
        premise_id (int): Unique identifier of the premise (path parameter).
        db (PremiseService): Premise service injected via dependency.

    Returns:
        PremiseResponse: Detailed information about the premise.
    """
    return await db.get_premise_by_id(premise_id)


@router.get(
    "/city/{premise_city}",
    response_model=list[ShortPremiseResponse],
    status_code=status.HTTP_200_OK,
)
async def get_premises_by_city(
    premise_city: str, db: PremiseService = Depends(get_premise_service)
):
    """Returns all premises located in the given city.

    Args:
        premise_city (str): Name of the city to search in (path parameter).
        db (PremiseService): Premise service injected via dependency.

    Returns:
        list[ShortPremiseResponse]: Short representations of the premises
            found in the city.
    """
    return await db.get_premises_by_city(premise_city)


@router.post(
    "/new", response_model=PremiseResponse, status_code=status.HTTP_201_CREATED
)
async def create_premise(
    address: AddressCreate,
    features: FeatureCreate,
    premise_data: PremiseCreate,
    current_user: CurrentUser,
    db: PremiseService = Depends(get_premise_service),
):
    """Creates a new premise owned by the current user.

    The authenticated user becomes the landlord of the new premise.

    Args:
        address (AddressCreate): Address data of the premise (request body).
        features (FeatureCreate): Features and amenities of the premise (request body).
        premise_data (PremiseCreate): Core premise details (request body).
        current_user (CurrentUser): Authenticated user, used as the landlord.
        db (PremiseService): Premise service injected via dependency.

    Returns:
        PremiseResponse: The newly created premise (HTTP 201).
    """
    return await db.create_premise(address, features, current_user.id, premise_data)


@router.delete("/{premise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_premise(
    premise_id: int,
    current_user: CurrentUser,
    db: PremiseService = Depends(get_premise_service),
):
    """Deletes a premise owned by the current user.

    Args:
        premise_id (int): Unique identifier of the premise to delete
            (path parameter).
        current_user (CurrentUser): Authenticated user; must be the landlord
            of the premise.
        db (PremiseService): Premise service injected via dependency.

    Returns:
        None: An empty response with status 204 on success.
    """
    await db.delete_premise(premise_id, current_user.id)


@router.patch(
    "/{premise_id}", response_model=PremiseResponse, status_code=status.HTTP_200_OK
)
async def update_premise(
    premise_id: int,
    premise_data: PremiseUpdate,
    current_user: CurrentUser,
    db: PremiseService = Depends(get_premise_service),
):
    """Partially updates a premise owned by the current user.

    Args:
        premise_id (int): Unique identifier of the premise to update (path parameter).
        premise_data (PremiseUpdate): Fields to update (request body).
        current_user (CurrentUser): Authenticated user; must be the landlord of the premise.
        db (PremiseService): Premise service injected via dependency.

    Returns:
        PremiseResponse: The premise returned by the service.
    """
    return await db.update_premise_by_id(premise_id, premise_data, current_user.id)
