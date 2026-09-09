from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import text

from app.database.database import engine

@asynccontextmanager
async def lifespan(app : FastAPI):

    async with engine.begin() as connection:
        await connection.execute(text("SELECT 1"))

    yield

    await connection.dispose()

app = FastAPI(
    title="DataPulse",
    description="Data Analysis Platform",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message" : "hehehe"
    }