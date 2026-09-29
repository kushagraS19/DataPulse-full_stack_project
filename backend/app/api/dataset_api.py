from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user_model import User
from app.schemas.dataset_schema import (
    DatasetCreate,
    DatasetResponse
)
from app.services.dataset_services import (
    create_dataset,
    get_project_datasets
)

from app.services.project_services import get_project_by_id
from app.services.workspace_services import get_workspace_by_id


router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"]
)


@router.post(
    "/",
    response_model=DatasetResponse
)
async def create_new_dataset(
    data: DatasetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    project = await get_project_by_id(
        db,
        data.project_id,
        data.workspace_id
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

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

    dataset = await create_dataset(
        db,
        data.project_id,
        data.name,
        data.file_path
    )

    return dataset


@router.get(
    "/workspace/{workspace_id}/project/{project_id}",
    response_model=list[DatasetResponse]
)
async def get_datasets(
    workspace_id: int,
    project_id: int,
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

    datasets = await get_project_datasets(
        db,
        project_id
    )

    return datasets