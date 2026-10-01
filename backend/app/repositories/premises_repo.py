from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.premises_model import Premise, PremiseAddress


class PremiseRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_premise_by_id(self, premise_id: int):
        stmt = select(Premise).where(Premise.id == premise_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_premises_by_city(self, premise_city: str):
        stmt = (
            select(Premise)
            .join(Premise.address)
            .where(PremiseAddress.city == premise_city)
            .options(selectinload(Premise.address))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
