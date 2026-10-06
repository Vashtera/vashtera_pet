from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.premises_model import Premise, PremiseAddress, PremiseFeature
from ..schemas.premises_scheme import (
    FeatureResponse,
    FullAddressResponse,
    PremiseCreate,
)


class PremiseRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_premise_by_id(self, premise_id: int):
        stmt = (
            select(Premise)
            .where(Premise.id == premise_id)
            .options(
                selectinload(Premise.landlord),
                selectinload(Premise.address),
                selectinload(Premise.feature),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_premises_by_city(self, premise_city: str):
        stmt = (
            select(Premise)
            .join(Premise.address)
            .where(PremiseAddress.city == premise_city)
            .options(
                selectinload(Premise.landlord),
                selectinload(Premise.address),
                selectinload(Premise.feature),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_premise(
        self,
        address: FullAddressResponse,
        features: FeatureResponse,
        premise_data: PremiseCreate,
    ):
        db_address = PremiseAddress(**address.model_dump())
        self.session.add(db_address)
        db_features = PremiseFeature(**features.model_dump())
        self.session.add(db_features)
        try:
            db_premise = Premise(
                address=db_address, feature=db_features, **premise_data.model_dump()
            )
            self.session.add(db_premise)
            await self.session.commit()
            await self.session.refresh(db_premise)
        except Exception as e:
            await self.session.rollback()
            raise e  # noqa: TRY201
