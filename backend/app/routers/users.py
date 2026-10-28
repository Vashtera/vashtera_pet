from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from ..auth import CurrentUser, create_access_token
from ..core.config import settings
from ..database import get_db
from ..schemas.users_scheme import Token, UserCreate, UserPrivate, UserTopUpBalance
from ..services.users_service import UserService

router = APIRouter()


def get_user_service(session=Depends(get_db)):
    return UserService(session)


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


@router.post("/{user_id}/top-up", status_code=status.HTTP_200_OK)
async def top_up_balance(
    user: CurrentUser,
    top_up_amount: UserTopUpBalance,
    db: UserService = Depends(get_user_service),
) -> None:
    """
    This function is only intended to top up virtual money for
    the purpose of gaining experience using the platform.
    In the future, I may add real escrow payments.

    Args:
        user - this is a registered user who has passed the verification in `auth.py`.
        top_up_amount - Balance top-up schema containing only the `amount` field
    """
    await db.top_up_balance(user.id, top_up_amount)
