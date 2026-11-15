import os

from sqlalchemy.engine import make_url

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

TEST_URL = os.environ["TEST_DATABASE_URL"]
_url = make_url(TEST_URL)
TEST_DB_NAME = _url.database
ADMIN_URL = _url.set(database="postgres")

os.environ["DATABASE_URL"] = TEST_URL
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
import pytest
from database import Base, get_db
from httpx import ASGITransport, AsyncClient
from main import app
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def test_engine():
    admin = create_async_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
    async with admin.connect() as conn:
        exists = await conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": TEST_DB_NAME},
        )
        if not exists:
            await conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    await admin.dispose()

    engine = create_async_engine(TEST_URL, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def setup_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


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
    yield

    tables = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
    await db_session.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE"))
    await db_session.commit()
