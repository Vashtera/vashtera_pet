from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import hash_password
from ..models.users_model import User
from ..schemas.users_scheme import UserCreate


class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get user by his id

        Args:
            user_id: int, the ID of the user we want to retrieve

        Returns:
            Returns the user according to the `UserPublic` or `UserPrivate` schema or None
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_user_by_email(self, user_email: str) -> User | None:
        """
        Get user by his email | username

        Args:
            user_email: str, the email | username of the user we want to retrieve

        Returns:
            Returns the user according to the `UserPublic` or `UserPrivate` schema or None
        """
        stmt = select(User).where(User.email == user_email.lower())
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Get user by his username

        Args:
            user_email: str, the username of the user we want to retrieve

        Returns:
            Returns the user according to the `UserPublic` or `UserPrivate` schema or None
        """
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_user(self, user_data: UserCreate) -> User | None:
        """
        Creating a user based on the data provided according to the UserCreate schema

        Args:
            user_data: `UserCreate` schema containing `username`, `email`, `contact_number`, and `hash_password`

        Returns:
            The `User` model with the provided data is expected to be returned if no exceptions occur.
            If an exception occurs, the transaction will be rolled back using `.rollback()`
        """
        try:
            new_user = User(
                username=user_data.username,
                email=user_data.email,
                contact_number=user_data.contact_number,
                password_hash=hash_password(user_data.password),
            )
            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
            return new_user
        except Exception:
            await self.session.rollback()
            raise

    async def top_up_balance(self, user_id: int, sum: )