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

    unique_filename = (
        f"{uuid.uuid4()}_{file.filename}"
    )

    file_path = os.path.join(
        "uploads",
        unique_filename
    )

    file_size = 0

    with open(file_path, "wb") as buffer:

        while chunk := await file.read(1024 * 1024):

            file_size += len(chunk)

            if file_size > MAX_FILE_SIZE:

                os.remove(file_path)

                raise HTTPException(
                    status_code=400,
                    detail="File size must be less than 50 MB"
                )

            buffer.write(chunk)

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8",
            newline=""
        ) as csv_file:

            reader = csv.reader(csv_file)
            rows = list(reader)

            if not rows:
                os.remove(file_path)

                raise HTTPException(
                    status_code=400,
                    detail="CSV file is empty"
                )

            if len(rows) < 2:
                os.remove(file_path)

                raise HTTPException(
                    status_code=400,
                    detail="CSV file must contain a header and at least one data row"
                )

    except UnicodeDecodeError:

        os.remove(file_path)

        raise HTTPException(
            status_code=400,
            detail="CSV file must be UTF-8 encoded"
        )

    except csv.Error:

        os.remove(file_path)

        raise HTTPException(
            status_code=400,
            detail="Invalid CSV file"
        )

    dataset = await create_dataset(
        db,
        project_id,
        file.filename,
        file_path
    )

    return dataset