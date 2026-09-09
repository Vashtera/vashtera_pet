from contextlib import asynccontextmanager

from app.database import engine
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield  # engine initialised at module level
    await engine.dispose()  # drain pool on shutdown


app = FastAPI()
