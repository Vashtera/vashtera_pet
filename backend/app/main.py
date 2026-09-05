from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan():
    yield


app = FastAPI()
