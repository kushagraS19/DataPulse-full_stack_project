
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.database.database import engine
from app.models.base import Base
from app.models.user_model import User  # Ensures User is registered with Base.metadata.

from app.api.user_api import router as user_router
from app.api.auth_api import router as auth_router
from app.api.workspace_api import router as workspace_router
from app.api.project_api import router as project_router
from app.api.dataset_api import router as dataset_router
from app.api.analytics_api import router as analytics_router
from app.api.dashboard_api import router as dashboard_router
from app.api.chart_api import router as chart_router
from app.api.insight_api import router as insight_router

from app.core.security_headers import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as connection:
            await connection.execute(text("SELECT 1"))

            # Create tables automatically only during local development.
            # Production schema changes must use Alembic migrations.
            if settings.ENVIRONMENT.lower() == "development":
                await connection.run_sync(Base.metadata.create_all)

        yield
    finally:
        await engine.dispose()


app = FastAPI(
    title="DataPulse",
    description="Data Analysis Platform",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)

app.add_middleware(SecurityHeadersMiddleware)


@app.get("/")
async def root():
    return {"message": "DataPulse API is running"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(workspace_router)
app.include_router(project_router)
app.include_router(dataset_router)
app.include_router(analytics_router)
app.include_router(dashboard_router)
app.include_router(chart_router)
app.include_router(insight_router)
