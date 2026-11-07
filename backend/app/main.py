import logging

logging.basicConfig(level=logging.INFO)
from contextlib import asynccontextmanager

from database import engine
from fastapi import FastAPI
from routers.bookings import router as bookings_router
from routers.premises import router as premise_router
from routers.users import router as users_router
from services.scheduler_service import scheduler


@asynccontextmanager
async def lifespan(_app: FastAPI):
    scheduler.start()  # starting the task scheduler
    try:
        yield
    finally:
        scheduler.shutdown()  # stop the scheduler first, so no job runs while closing the pool
        await engine.dispose()  # then drain the connection pool


app = FastAPI(lifespan=lifespan)

app.include_router(premise_router, prefix="/api/premises", tags=["premises"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(bookings_router, prefix="/api/bookings", tags=["bookings"])
