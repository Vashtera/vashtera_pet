import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_shop.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from ..database import Base, get_db
from ..main import app


@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(
        os.environ["DATABASE_URL"],
        poolclass=NullPool,
    )
    return engine


@pytest.fixture(scope="session")
async def setup_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine, setup_database):
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def concurrent_client(test_engine, setup_database):
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
async def clean_database(db_session):
    from sqlalchemy import delete

    from ..models.bookings_model import Booking
    from ..models.payments_model import Payment
    from ..models.premises_model import Premise, PremiseAddress, PremiseFeature
    from ..models.users_model import PasswordResetToken, User

    yield

    await db_session.execute(delete(Premise))
    await db_session.execute(delete(Booking))
    await db_session.execute(delete(User))
    await db_session.execute(delete(PasswordResetToken))
    await db_session.execute(delete(PremiseAddress))
    await db_session.execute(delete(PremiseFeature))
    await db_session.execute(delete(Payment))
    await db_session.commit()


async def create_test_user(
    client: AsyncClient,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "testpassword123",
) -> dict:
    response = await client.post(
        "/api/users",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201, f"Failed to create user: {response.text}"
    return response.json()


async def login_user(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "testpassword123",
) -> str:
    response = await client.post(
        "/api/users/token",
        data={
            "username": email,
            "password": password,
        },
    )
    assert response.status_code == 200, f"Failed to login: {response.text}"
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
