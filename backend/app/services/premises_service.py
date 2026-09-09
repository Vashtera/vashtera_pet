from app.repositories.premises_repo import PremiseRepo
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


class PremiseService:
    def __init__(self, db: AsyncSession):
        self.session = PremiseRepo(db)

    async def get_premise_by_id(self, premise_id: int):
        premise = self.session.get_premise_by_id(premise_id)
        if not premise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {premise_id} not founded",
            )
        return premise
