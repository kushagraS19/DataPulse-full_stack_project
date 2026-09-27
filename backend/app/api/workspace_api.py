from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.models.user_model import User
from app.schemas.workspace_schema import (
    WorkspaceCreate,
    WorkspaceResponse
)
from app.services.workspace_services import (
    create_workspace,
    get_user_workspaces
)


router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"]
)


@router.post(
    "/",
    response_model=WorkspaceResponse
)
async def create_new_workspace(
    data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    workspace = await create_workspace(
        db,
        current_user.id,
        data.name
    )

    return workspace


@router.get(
    "/",
    response_model=list[WorkspaceResponse]
)
async def get_my_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    workspaces = await get_user_workspaces(
        db,
        current_user.id
    )

    return workspaces