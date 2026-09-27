from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user_model import User
from app.schemas.project_schema import (
    ProjectCreate,
    ProjectResponse
)
from app.services.project_services import (
    create_project,
    get_workspace_projects,
)

from app.services.workspace_services import get_workspace_by_id


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


@router.post(
    "/",
    response_model=ProjectResponse
)
async def create_new_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    workspace = await get_workspace_by_id(
        db,
        data.workspace_id,
        current_user.id
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found"
        )

    project = await create_project(
        db,
        data.workspace_id,
        data.name
    )

    return project

@router.get(
    "/workspace/{workspace_id}",
    response_model=list[ProjectResponse]
)
async def get_projects(
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

    projects = await get_workspace_projects(
        db,
        workspace_id
    )

    return projects