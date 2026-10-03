from fastapi import APIRouter, Depends

from ..database import get_db
from ..schemas.premises_scheme import PremiseResponse
from ..services.premises_service import PremiseService

router = APIRouter()


def get_premise_service(session=Depends(get_db)):
    return PremiseService(session)


@router.get("/{premise_id}")
async def get_premise_by_id(
    premise_id: int, db: PremiseService = Depends(get_premise_service)
):
    return await db.get_premise_by_id(premise_id)


# TEMPORARY
@router.get("/city/{premise_city}")
async def get_premises_by_city(
    premise_city: str, db: PremiseService = Depends(get_premise_service)
):
    return await db.get_premises_by_city(premise_city)
