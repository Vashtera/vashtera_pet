from typing import Optional

from app.models.premises_model import Premise
from app.schemas.premises_scheme import PremisePublic
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class PremiseRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_premise_by_id(self, premise_id: int):
        stmt = select(Premise).where(Premise.id == premise_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
