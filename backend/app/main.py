from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text

from app.database.database import engine

from app.models.base import Base
from app.models.user_model import User

from app.api.user_api import router as user_router
from app.api.auth_api import router as auth_router

from app.core.security_headers import SecurityHeadersMiddleware

@asynccontextmanager
async def lifespan(app : FastAPI):

    async with engine.begin() as connection:
        await connection.execute(text("SELECT 1"))

        await connection.run_sync(
            Base.metadata.create_all
        )

    yield

    await engine.dispose()
app = FastAPI(
    title="DataPulse",
    description="Data Analysis Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(
    SecurityHeadersMiddleware
)

@app.get("/")
async def root():
    return {
        "message" : "hehehe"
    }

app.include_router(user_router)
app.include_router(auth_router)