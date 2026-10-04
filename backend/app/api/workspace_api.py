from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.models.user_model import User

from app.schemas.workspace_schema import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse
)

from app.services.workspace_services import (
    create_workspace,
    get_user_workspaces,
    update_workspace,
    delete_workspace
)


router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"]
)


# CREATE NEW WORKSPACE
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


# GET MY WORKSPACE
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


# UPDATE WORKSPACE
@router.patch(
    "/{workspace_id}",
    response_model=WorkspaceResponse
)
async def update_my_workspace(
    workspace_id: int,
    data: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    workspace = await update_workspace(
        db,
        workspace_id,
        current_user.id,
        data.name
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found"
        )

    return workspace


# DELETE WORKSPACE
@router.delete(
    "/{workspace_id}",
    response_model=WorkspaceResponse
)
async def delete_my_workspace(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    workspace = await delete_workspace(
        db,
        workspace_id,
        current_user.id
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found"
        )

    return workspace


