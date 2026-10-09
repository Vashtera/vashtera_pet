from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import verify_password
from ..repositories.users_repo import UserRepo
from ..schemas.users_scheme import UserCreate


class UserService:
    def __init__(self, db: AsyncSession):
        self.session = UserRepo(db)

    async def register(self, user: UserCreate):
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
        user = await self.session.get_user_by_email(form_data.username)
        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User or password not exist",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
