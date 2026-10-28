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
    """Provide a `UserService` instance for request handlers.

    FastAPI dependency that builds a `UserService` on top of the database
    session for the current request.

    Args:
        session (AsyncSession): Database session injected via the `get_db`
            dependency.

    Returns:
        UserService: A service object bound to the given session, used by
            route handlers to work with user data.
    """
    return UserService(session)


@router.post("/auth/sign-up", response_model=UserPrivate)
async def create_user(user: UserCreate, db: UserService = Depends(get_user_service)):
    """Register a new user account.

    Validates the incoming registration data and delegates account creation
    to the user service.

    Args:
        user (UserCreate): Registration payload parsed from the JSON request body.
        db (UserService): User service used to create the account.
            Injected via the `get_user_service` dependency.

    Returns:
        UserPrivate: The newly created user, serialized with the private
            response schema.

    Raises:
        HTTPException: If registration fails, for example when a user with
            the same username or email already exists. Raised inside
            `UserService.register`.
    """
    return await db.register(user)


@router.post("/auth/sign-in", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: UserService = Depends(get_user_service),
):
    """Authenticate a user and issue a JWT access token.

    Accepts credentials in the OAuth2 password flow format
    (application/x-www-form-urlencoded), verifies them through the user
    service, and creates an access token whose `sub` claim contains the
    user's ID.

    Args:
        form_data (OAuth2PasswordRequestForm): Login form data: `username`
            and `password` (plus optional OAuth2 fields such as `scope`).
        db (UserService): User service used to authenticate the user.
            Injected via the `get_user_service` dependency.

    Returns:
        Token: An object with the following fields:
            - access_token (str): signed JWT whose `sub` claim is `str(user.id)`;
            - token_type (str): always `"bearer"`.

    Raises:
        HTTPException: If authentication fails (invalid username or
            password). Raised inside `UserService.authenticate_user`.

    Note:
        The token lifetime is controlled by the
        `settings.access_token_expire_minutes` setting.
    """
    user = await db.authenticate_user(form_data)

    # Create access token with user_id as subject
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
        user - this is a registered user who has passed the verification in `auth.py`
        top_up_amount - Balance top-up schema containing only the `amount` field
        db - Dependency that passes the user's session to the service
    """
    await db.top_up_balance(user.id, top_up_amount)
