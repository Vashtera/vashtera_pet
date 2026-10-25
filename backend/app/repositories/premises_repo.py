from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.premises_model import Premise, PremiseAddress, PremiseFeature
from ..models.users_model import User
from ..schemas.premises_scheme import (
    AddressCreate,
    FeatureCreate,
    PremiseCreate,
    PremiseUpdate,
)


class PremiseRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_premises(self) -> list[Premise]:
        """
        Get a list of all premises from the database

        Args:
            -

        Returns:
            A list of all premises
        """
        stmt = select(Premise).options(
            selectinload(Premise.landlord),
            selectinload(Premise.address),
            selectinload(Premise.feature),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_premise_by_id(self, premise_id: int) -> Premise | None:
        """
        Get premise by id

        Args:
            premise_id: int, the ID of the premise we want to retrieve

        Returns:
            Return the premises model or None
        """
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

    async def get_premises_by_city(self, premise_city: str) -> list[Premise]:
        """
        Get premise by city

        Args:
            premise_city: str, the city where the premises are located

        Return:
            a list of premises
        """
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
        address: AddressCreate,
        features: FeatureCreate,
        landlord: int,
        premise_data: PremiseCreate,
    ):
        """
        Create a premise for authorizated user

        Args:
            address: schema containing street, city, district, and house_number for create
            features: schema containing an optional `image`, an optional `floor`, `area`, `rooms`, and `price`
            landlord: the ID of the user we want to retrieve
            premise_data: schema containing `premise_type` with Literal list of types, an optional `description` and `contact_number`

        Returns:
            Premise model
        """
        try:
            db_address = PremiseAddress(**address.model_dump())
            self.session.add(db_address)
            db_features = PremiseFeature(**features.model_dump())
            self.session.add(db_features)
            db_premise = Premise(
                address=db_address,
                feature=db_features,
                landlord_id=landlord,
                **premise_data.model_dump(),
            )
            self.session.add(db_premise)
            await self.session.commit()
            await self.session.refresh(db_premise)
            # We need to retrieve the newly created premise and return it
            premise = await self.get_premise_by_id(db_premise.id)
            return premise
        except Exception:
            await self.session.rollback()
            raise

    async def delete_premise_by_id(self, premise_id: int) -> None:
        """
        Delete premise by id

        Args:
            premise_id: int, the ID of the premise we want to retrieve for delete only

        Returns:
            None
        """
        premise = await self.get_premise_by_id(premise_id)
        await self.session.delete(premise)
        await self.session.commit()

    async def update_premise_by_id(
        self, premise_id: int, premise_data: PremiseUpdate
    ) -> Premise:
        """
        Update a premise by premise_id using the provided data

        Args:
            premise_id: int, the ID of the premise we want to update
            premise_data: schema containing an optional `description`, `contact_number` and `premise_type` with literal list of types

        Returns:
            Updated premise
        """
        premise = await self.get_premise_by_id(premise_id)
        # exclude_unset - used to modify only those parameters passed by the user
        # The provided parameters are converted into a dictionary.
        # Then, a loop uses the setattr() function to pass the premise, the name of the attribute to update,and the new value.
        # It automatically replaces the existing values, which are then committed to the database
        update_data = premise_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(premise, field, value)

        await self.session.commit()
        # This line is needed to load the landlord data into this table because
        # it is not available in the current variable.
        # We use attribute_names to fetch this information for the Response
        await self.session.refresh(premise, attribute_names=["landlord"])
        return premise

    async def get_premise_landlord(self, premise_id: int) -> User | None:
        """
        Get the landlord of a premise by premise_id

        Args:
            premise_id: int, the ID of the premise we want to retrieve

        Returns:
            User model or `None`
        """
        stmt = (
            select(User)
            .where(Premise.id == premise_id)
            .options(selectinload(Premise.landlord))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
