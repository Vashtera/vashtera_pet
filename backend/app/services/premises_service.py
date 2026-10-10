from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.premises_repo import PremiseRepo
from ..repositories.users_repo import UserRepo
from ..schemas.premises_scheme import (
    FeatureResponse,
    FullAddressResponse,
    PremiseCreate,
)


class PremiseService:
    def __init__(self, db: AsyncSession):
        self.session = PremiseRepo(db)

    async def get_premise_by_id(self, premise_id: int):
        premise = await self.session.get_premise_by_id(premise_id)
        if not premise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Premise with id {premise_id} not founded",
            )
        return premise

    async def get_premises_by_city(self, premise_city: str) -> str:
        premises = await self.session.get_premises_by_city(premise_city)
        if not premises:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"City {premise_city} not founded",
            )
        return premises

    async def create_premise(
        self,
        address: FullAddressResponse,
        features: FeatureResponse,
        landlord_id: int,
        premise_data: PremiseCreate,
    ):
        premise = await self.session.create_premise(
            address, features, landlord_id, premise_data
        )
        return premise

    async def delete_premise(self, premise_id: int, user_id: int):
        premise = await self.session.get_premise_by_id(premise_id)
        if not premise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Premise not found",
            )

        if premise.landlord_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Premise not found",
            )

        await self.session.delete_premise_by_id(premise_id)
