from fastapi import APIRouter, Depends

from ..database import get_db
from ..schemas.premises_scheme import PremisePublic
from ..services.premises_service import PremiseService

router = APIRouter()


def get_premise_service(session=Depends(get_db)):
    return PremiseService(session)


@router.get("premises/{premise_id}", response_model=PremisePublic)
async def get_premise_by_id(
    premise_id: int, db: PremiseService = Depends(get_premise_service)
):
    return db.get_premise_by_id(premise_id)
