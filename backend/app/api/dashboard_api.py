from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.database import get_db

from app.models.user_model import User

from app.schemas.dashboard_schema import (
    DashboardCreate,
    DashboardResponse
)

from app.services.dashboard_services import (
    create_dashboard,
    get_project_dashboards
)

from app.services.workspace_services import (
    get_workspace_by_id
)

from app.services.project_services import (
    get_project_by_id
)


router = APIRouter(
    prefix="/dashboards",
    tags=["Dashboards"]
)


@router.post(
    "/",
    response_model=DashboardResponse
)
async def create_dashboard_endpoint(
    dashboard_data: DashboardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    workspace = await get_workspace_by_id(
        db,
        dashboard_data.workspace_id,
        current_user.id
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found"
        )

    project = await get_project_by_id(
        db,
        dashboard_data.project_id,
        dashboard_data.workspace_id
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    dashboard = await create_dashboard(
        db,
        dashboard_data.project_id,
        dashboard_data.name
    )

    return dashboard


@router.get(
    "/project/{project_id}",
    response_model=list[DashboardResponse]
)
async def get_project_dashboards_endpoint(
    project_id: int,
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    workspace = await get_workspace_by_id(
        db,
        workspace_id,
        current_user.id
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found"
        )

    project = await get_project_by_id(
        db,
        project_id,
        workspace_id
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    dashboards = await get_project_dashboards(
        db,
        project_id
    )

    return dashboards


