from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)
from sqlalchemy.ext.asyncio import AsyncSession

import os
import uuid
import csv

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user_model import User
from app.schemas.dataset_schema import (
    DatasetCreate,
    DatasetResponse,
    DatasetPreviewResponse
)
from app.services.dataset_services import (
    create_dataset,
    get_project_datasets,
    preview_dataset
)

from app.services.project_services import get_project_by_id
from app.services.workspace_services import get_workspace_by_id
from app.services.data_processing_services import process_csv


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

    # Create raw and processed directories
    os.makedirs(
        "uploads/raw",
        exist_ok=True
    )

    os.makedirs(
        "uploads/processed",
        exist_ok=True
    )

    # Generate unique filename
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

    # Save raw uploaded file
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

    # Process raw CSV
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

    # Save processed CSV
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

    # Create database record
    dataset = await create_dataset(
        db,
        project_id,
        file.filename,
        processed_file_path
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