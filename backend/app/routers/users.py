from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from ..auth import create_access_token
from ..core.config import settings
from ..database import get_db
from ..schemas.users_scheme import Token, UserCreate, UserPrivate
from ..services.users_service import UserService

router = APIRouter()


async def get_user_service(session=Depends(get_db)):
    return await UserService(session)


@router.post("", response_model=UserPrivate)
async def create_user(user: UserCreate, db: UserService = Depends(get_user_service)):
    return await db.register(user)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: UserService = Depends(get_user_service),
):
    user = await db.authenticate_user(form_data)

    # Create access token with user id as subject
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")
