from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from backend.app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    pool_size=20,  # persistent connections per process
    max_overflow=10,  # burst connections
    pool_recycle=1800,  # Close and replace connections older than 30 minutes
    pool_pre_ping=True,  # issue SELECT 1 before handing out stale connections
    echo=True,  # TODO TEMPORARY TRUE
)

AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # prevents DetachedInstanceError when accessing
)


class Base(DeclarativeBase):
    pass


# AsyncSessionFactory context manager commits or rolls back here
async def get_db():
    async with AsyncSessionFactory() as session:
        yield session
