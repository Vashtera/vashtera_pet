import logging

from fastapi import HTTPException, status
from repositories.premises_repo import PremiseRepo
from schemas.premises_scheme import (
    AddressCreate,
    FeatureCreate,
    PremiseCreate,
    PremiseUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class PremiseService:
    def __init__(self, db: AsyncSession):
        self.session = PremiseRepo(db)

    async def get_all_premises(self):
        return await self.session.get_all_premises()

    async def get_premise_by_id(self, premise_id: int):
        """Retrieves a premise by its identifier.

        Queries the database layer and returns the matching premise.
        If no premise with the given identifier exists, raises an HTTP
        exception with a 404 status.

        Args:
            premise_id (int): Unique identifier of the premise.

        Returns:
            The premise object found in the database.

        Raises:
            HTTPException: With status 404 (NOT FOUND) if no premise
                with the given `premise_id` exists.
        """
        premise = await self.session.get_premise_by_id(premise_id)
        if not premise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Premise with id {premise_id} not founded",
            )
        return premise

    async def get_premises_by_city(self, premise_city: str) -> list:
        """Retrieves premises located in the specified city.

        Queries the database layer and returns the matching premises.
        If no premises are found for the city (or the city does not exist),
        raises an HTTP exception with a 404 status.

        Args:
            premise_city (str): Name of the city to search premises in.

        Returns:
            The premises found in the specified city.

        Raises:
            HTTPException: With status 404 (NOT FOUND) if no premises
                are found for `premise_city`.
        """
        premises = await self.session.get_premises_by_city(premise_city)
        if not premises:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"City {premise_city} not founded",
            )
        return premises

    async def create_premise(
        self,
        address: AddressCreate,
        features: FeatureCreate,
        landlord_id: int,
        premise_data: PremiseCreate,
    ):
        """Creates a new premise.

        Delegates persistence to the database layer, passing the address,
        features, landlord and premise details, and returns the newly
        created premise.

        Args:
            address (AddressCreate): Full address data of the premise.
            features (FeatureCreate): Features and amenities of the premise.
            landlord_id (int): Identifier of the landlord who owns the premise.
            premise_data (PremiseCreate): Data required to create the premise.

        Returns:
            The newly created premise object.
        """
        premise = await self.session.create_premise(
            address, features, landlord_id, premise_data
        )
        return premise

    async def delete_premise(self, premise_id: int, user_id: int) -> None:
        """Deletes a premise owned by the given user.

        Verifies that the premise exists and that the requesting user is its
        landlord before deleting it. For security, the same "Premise not found"
        message is used for both the missing and the not-owned cases.

        Args:
            premise_id (int): Unique identifier of the premise to delete.
            user_id (int): Identifier of the user requesting the deletion.
                Must match the premise's `landlord_id`.

        Raises:
            HTTPException: With status 404 (NOT FOUND) if no premise with the
                given `premise_id` exists.
            HTTPException: With status 403 (FORBIDDEN) if the premise belongs
                to a different landlord than `user_id`.
        """
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

    async def update_premise_by_id(
        self, premise_id: int, premise_data: PremiseUpdate, user_id: int
    ):
        """Updates a premise owned by the given user.

        Verifies that the premise exists and that the requesting user is its
        landlord, then applies the provided changes. For security, the same
        "Premise not found" message is used for both the missing and the
        not-owned cases.

        Args:
            premise_id (int): Unique identifier of the premise to update.
            premise_data (PremiseUpdate): Fields to update on the premise.
            user_id (int): Identifier of the user requesting the update.
                Must match the premise's `landlord_id`.

        Returns:
            The premise object as it was retrieved before the update was
            applied.

        Raises:
            HTTPException: With status 404 (NOT FOUND) if no premise with the
                given `premise_id` exists.
            HTTPException: With status 403 (FORBIDDEN) if the premise belongs
                to a different landlord than `user_id`.
            HTTPException: With status 422 (UNPROCESSABLE CONTENT) if the
                premise type is invalid.
        """
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

        if status.HTTP_422_UNPROCESSABLE_CONTENT:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Invalid premise type",
            )

        await self.session.update_premise_by_id(premise_id, premise_data)
        return premise
