from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import os
import uuid

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.dataset_model import Dataset
from app.models.user_model import User
from app.schemas.dataset_schema import (
    DatasetCreate,
    DatasetResponse,
    DatasetPreviewResponse,
    DatasetUpdate
)
from app.services.dataset_services import (
    create_dataset,
    get_project_datasets,
    preview_dataset,
    get_dataset_data,
    create_dataset_table,
    get_dataset_columns,
    get_dataset_column_operations,
    delete_dataset,
    rename_dataset
)

from app.services.project_services import get_project_by_id
from app.services.workspace_services import get_workspace_by_id
from app.services.data_processing_services import process_csv
from app.services.data_profiling_services import profile_dataset


router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"]
)

MAX_FILE_SIZE = 50 * 1024 * 1024


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


@router.patch(
    "/{dataset_id}",
    response_model=DatasetResponse
)
async def rename_dataset_endpoint(
    dataset_id: int,
    data: DatasetUpdate,
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

    name = data.name.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Dataset name cannot be empty"
        )

    if len(name) > 255:
        raise HTTPException(
            status_code=400,
            detail="Dataset name must be 255 characters or less"
        )

    dataset = await rename_dataset(
        db,
        dataset_id,
        project_id,
        name
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
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


@router.post(
    "/upload",
    response_model=DatasetResponse
)
async def upload_dataset(
    project_id: int,
    workspace_id: int,
    file: UploadFile = File(...),
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

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )

    os.makedirs(
        "uploads/raw",
        exist_ok=True
    )

    os.makedirs(
        "uploads/processed",
        exist_ok=True
    )

    unique_id = str(uuid.uuid4())

    raw_file_path = os.path.join(
        "uploads",
        "raw",
        f"{unique_id}_{file.filename}"
    )

    processed_file_path = os.path.join(
        "uploads",
        "processed",
        f"{unique_id}_cleaned.csv"
    )

    file_size = 0

    with open(
        raw_file_path,
        "wb"
    ) as buffer:

        while chunk := await file.read(
            1024 * 1024
        ):
            file_size += len(chunk)

            if file_size > MAX_FILE_SIZE:

                os.remove(
                    raw_file_path
                )

                raise HTTPException(
                    status_code=400,
                    detail="File size must be less than 50 MB"
                )

            buffer.write(chunk)

    try:

        df = process_csv(
            raw_file_path
        )

    except ValueError as e:

        os.remove(
            raw_file_path
        )

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    try:

        df.to_csv(
            processed_file_path,
            index=False
        )

    except Exception as e:

        os.remove(
            raw_file_path
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save processed CSV: {str(e)}"
        )

    row_count = len(df)
    column_count = len(df.columns)

    dataset = await create_dataset(
        db,
        project_id,
        file.filename,
        processed_file_path,
        row_count=row_count,
        column_count=column_count,
        file_size=file_size
    )

    try:

        await create_dataset_table(
            db,
            dataset.id,
            df
        )

    except Exception as e:

        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create analytical table: {str(e)}"
        )

    return dataset


@router.get(
    "/project/{project_id}",
    response_model=list[DatasetResponse]
)
async def get_project_dataset_list(
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

    datasets = await get_project_datasets(
        db,
        project_id
    )

    return datasets


@router.delete(
    "/{dataset_id}",
)
async def delete_dataset_endpoint(
    dataset_id: int,
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

    try:
        result = await delete_dataset(
            db,
            dataset_id,
            project_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete dataset: {str(e)}"
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    return result


@router.get(
    "/{dataset_id}/preview",
    response_model=DatasetPreviewResponse
)
async def get_dataset_preview(
    dataset_id: int,
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

    try:
        preview = await preview_dataset(
            db,
            dataset_id,
            project_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    if preview is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    return preview


@router.get(
    "/{dataset_id}/data"
)
async def get_dataset_data_endpoint(
    dataset_id: int,
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

    try:
        result = await get_dataset_data(
            db,
            dataset_id,
            project_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    return result


@router.get(
    "/{dataset_id}/columns"
)
async def get_dataset_columns_endpoint(
    dataset_id: int,
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

    columns = await get_dataset_columns(
        db,
        dataset_id
    )

    if columns is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    return {
        "dataset_id": dataset_id,
        "columns": columns
    }


@router.get("/{dataset_id}/profile")
async def get_dataset_profile_endpoint(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.project_id == project_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:
        df = pd.read_csv(dataset.file_path)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read dataset: {str(e)}"
        )

    try:
        profile = profile_dataset(df)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to profile dataset: {str(e)}"
        )

    return {
        "dataset_id": dataset.id,
        "project_id": dataset.project_id,
        "name": dataset.name,
        "profile": profile
    }


@router.get(
    "/{dataset_id}/column-operations"
)
async def get_dataset_column_operations_endpoint(
    dataset_id: int,
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

    result = await get_dataset_column_operations(
        db,
        dataset_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    return {
        "dataset_id": dataset_id,
        "columns": result
    }