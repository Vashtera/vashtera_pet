from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import engine
from .routers.bookings import router as bookings_router
from .routers.premises import router as premise_router
from .routers.users import router as users_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield  # engine initialised at module level
    await engine.dispose()  # drain pool on shutdown


app = FastAPI()

app.include_router(premise_router, prefix="/api/premises", tags=["premises"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(bookings_router, prefix="/api/bookings", tags=["bookings"])
