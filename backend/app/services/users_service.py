import logging
from typing import Annotated

from core.security import verify_password
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from repositories.users_repo import UserRepo
from schemas.users_scheme import UserCreate, UserTopUpBalance
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: AsyncSession):
        self.session = UserRepo(db)

    async def register(self, user: UserCreate):
        """
        User creation function.

        Args:
            user - Validated data for user creation (`username`, `email`, `password`, `contact_number`).

        Returns:
            The created `User` object.

        Raises:
            HTTP_400 - In case the username and email already exist.
        """
        existing_username = await self.session.get_user_by_username(user.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exist",
            )

        existing_user_email = await self.session.get_user_by_email(user.email)
        if existing_user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exist",
            )

        return await self.session.create_user(user)

    async def authenticate_user(
        self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ):
        """
        Authentication service: user login using a hashed password function.

        Args:
            form_data - Look up user by email (case-insensitive)

        Note:
            OAuth2PasswordRequestForm uses "username" field, but we treat it as email

        Returns:
            Authenticated user.
        """
        user = await self.session.get_user_by_email(form_data.username)
        if not user or not verify_password(form_data.password, user.password_hash):
            # Verify user exists and password is correct
            # Don't reveal which one failed (security best practice)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User or password not exist",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    async def top_up_balance(
        self, user_id: int, top_up_amount: UserTopUpBalance
    ) -> None:
        """
        User top-up balance function.

        Args:
            user_id - User ID for balance top-up.
            top_up_amount - The balance top-up amount contained in the validated schema.
        """
        if top_up_amount.sum <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The top-up amount cannot be less than or equal to 0.",
            )
        await self.session.top_up_balance(user_id, top_up_amount)
