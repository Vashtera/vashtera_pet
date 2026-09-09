from contextlib import asynccontextmanager

from app.database import engine
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI()
