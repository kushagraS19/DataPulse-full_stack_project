from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
)

import logging
import os
import uuid

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.dataset_model import Dataset
from app.models.user_model import User
from app.schemas.dataset_schema import (
    DatasetCreate,
    DatasetResponse,
    DatasetPreviewResponse,
    DatasetUpdate,
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
    rename_dataset,
    _safe_dataset_file_path,
)
from app.services.project_services import get_project_by_id
from app.services.workspace_services import get_workspace_by_id
from app.services.data_processing_services import process_csv
from app.services.data_profiling_services import profile_dataset


router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"],
)

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 50 * 1024 * 1024


async def _validate_workspace_project(
    db: AsyncSession,
    workspace_id: int,
    project_id: int,
    user_id: int,
):
    """Verify that the user owns the workspace and the project belongs to it."""

    workspace = await get_workspace_by_id(
        db,
        workspace_id,
        user_id,
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found",
        )

    project = await get_project_by_id(
        db,
        project_id,
        workspace_id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project


async def _validate_dataset_ownership(
    db: AsyncSession,
    dataset_id: int,
    project_id: int,
):
    """Ensure a dataset belongs to the requested project."""

    result = await db.execute(
        select(Dataset.id).where(
            Dataset.id == dataset_id,
            Dataset.project_id == project_id,
        )
    )

    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )


@router.post(
    "/",
    response_model=DatasetResponse,
)
async def create_new_dataset(
    data: DatasetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _validate_workspace_project(
        db,
        data.workspace_id,
        data.project_id,
        current_user.id,
    )

    # This endpoint accepts only existing processed CSV files.
    # New uploads should use POST /datasets/upload.
    processed_root = os.path.realpath(
        os.path.join(os.getcwd(), "uploads", "processed")
    )
    supplied_path = os.path.realpath(data.file_path)

    try:
        is_inside_processed = (
            os.path.commonpath(
                [processed_root, supplied_path]
            )
            == processed_root
        )
    except ValueError:
        is_inside_processed = False

    if (
        not is_inside_processed
        or not supplied_path.lower().endswith(".csv")
        or not os.path.isfile(supplied_path)
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "file_path must reference an existing "
                "processed CSV upload"
            ),
        )

    stored_file_path = os.path.relpath(
        supplied_path,
        os.getcwd(),
    )

    existing_result = await db.execute(
        select(Dataset.id)
        .where(
            Dataset.file_path.in_(
                [
                    data.file_path,
                    stored_file_path,
                    supplied_path,
                ]
            )
        )
        .limit(1)
    )

    if existing_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=409,
            detail="This file is already linked to a dataset",
        )

    try:
        dataset = await create_dataset(
            db,
            data.project_id,
            data.name,
            stored_file_path,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except Exception:
        logger.exception("Failed to create dataset")
        raise HTTPException(
            status_code=500,
            detail="Failed to create dataset",
        ) from None

    return dataset


@router.patch(
    "/{dataset_id}",
    response_model=DatasetResponse,
)
async def rename_dataset_endpoint(
    dataset_id: int,
    data: DatasetUpdate,
    project_id: int,
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _validate_workspace_project(
        db,
        workspace_id,
        project_id,
        current_user.id,
    )

    name = data.name.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Dataset name cannot be empty",
        )

    if len(name) > 255:
        raise HTTPException(
            status_code=400,
            detail="Dataset name must be 255 characters or less",
        )

    dataset = await rename_dataset(
        db,
        dataset_id,
        project_id,
        name,
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    return dataset


@router.get(
    "/workspace/{workspace_id}/project/{project_id}",
    response_model=list[DatasetResponse],
)
async def get_datasets(
    workspace_id: int,
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _validate_workspace_project(
        db,
        workspace_id,
        project_id,
        current_user.id,
    )

    return await get_project_datasets(
        db,
        project_id,
    )


@router.post(
    "/upload",
    response_model=DatasetResponse,
)
async def upload_dataset(
    project_id: int,
    workspace_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _validate_workspace_project(
        db,
        workspace_id,
        project_id,
        current_user.id,
    )

    original_filename = (
        (file.filename or "upload.csv")
        .replace("\\", "/")
        .rsplit("/", 1)[-1]
    )

    if (
        not original_filename
        or not original_filename.lower().endswith(".csv")
    ):
        await file.close()
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed",
        )

    os.makedirs("uploads/raw", exist_ok=True)
    os.makedirs("uploads/processed", exist_ok=True)

    unique_id = str(uuid.uuid4())

    raw_file_path = os.path.join(
        "uploads",
        "raw",
        f"{unique_id}_{original_filename}",
    )

    processed_file_path = os.path.join(
        "uploads",
        "processed",
        f"{unique_id}_cleaned.csv",
    )

    file_size = 0
    dataset = None
    upload_succeeded = False

    try:
        # Stream the upload to disk and enforce the size limit.
        with open(raw_file_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                file_size += len(chunk)

                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File size must not exceed 50 MB",
                    )

                buffer.write(chunk)

        try:
            df = process_csv(raw_file_path)

        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            ) from exc

        except Exception:
            logger.exception(
                "Failed to process uploaded CSV"
            )
            raise HTTPException(
                status_code=400,
                detail="Failed to process uploaded CSV",
            ) from None

        try:
            df.to_csv(
                processed_file_path,
                index=False,
            )

        except Exception:
            logger.exception(
                "Failed to save processed CSV"
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to save processed CSV",
            ) from None

        # create_dataset commits its own transaction.
        dataset = await create_dataset(
            db,
            project_id,
            original_filename,
            processed_file_path,
            row_count=len(df),
            column_count=len(df.columns),
            file_size=file_size,
        )

        try:
            await create_dataset_table(
                db,
                dataset.id,
                df,
            )

        except Exception:
            logger.exception(
                "Failed to create analytical table for dataset %s",
                dataset.id,
            )

            await db.rollback()

            # Explicitly clean up the committed dataset if table creation
            # fails. delete_dataset also removes the processed file after
            # successful database deletion.
            try:
                await delete_dataset(
                    db,
                    dataset.id,
                    project_id,
                )
            except Exception:
                logger.exception(
                    "Failed to clean up dataset %s after upload failure",
                    dataset.id,
                )

            raise HTTPException(
                status_code=500,
                detail="Failed to create analytical table",
            ) from None

        upload_succeeded = True
        return dataset

    except HTTPException:
        raise

    except Exception:
        logger.exception("Dataset upload failed")

        raise HTTPException(
            status_code=500,
            detail="Dataset upload failed",
        ) from None

    finally:
        await file.close()

        # The original upload is temporary.
        if os.path.exists(raw_file_path):
            try:
                os.remove(raw_file_path)
            except OSError:
                logger.exception(
                    "Could not remove raw upload file: %s",
                    raw_file_path,
                )

        # Keep the processed CSV only when the entire upload succeeds.
        if (
            not upload_succeeded
            and os.path.exists(processed_file_path)
        ):
            try:
                os.remove(processed_file_path)
            except OSError:
                logger.exception(
                    "Could not remove processed upload file: %s",
                    processed_file_path,
                )


@router.get(
    "/project/{project_id}",
    response_model=list[DatasetResponse],
)
async def get_project_dataset_list(
    project_id: int,
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _validate_workspace_project(
        db,
        workspace_id,
        project_id,
        current_user.id,
    )

    return await get_project_datasets(
        db,
        project_id,
    )


@router.delete("/{dataset_id}")
async def delete_dataset_endpoint(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _validate_workspace_project(
        db,
        workspace_id,
        project_id,
        current_user.id,
    )

    try:
        result = await delete_dataset(
            db,
            dataset_id,
            project_id,
        )

    except ValueError:
        logger.exception(
            "Dataset deletion failed for dataset %s",
            dataset_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to delete dataset",
        ) from None

    except Exception:
        logger.exception(
            "Dataset deletion failed for dataset %s",
            dataset_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to delete dataset",
        ) from None

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    return result


@router.get(
    "/{dataset_id}/preview",
    response_model=DatasetPreviewResponse,
)
async def get_dataset_preview(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _validate_workspace_project(
        db,
        workspace_id,
        project_id,
        current_user.id,
    )

    try:
        preview = await preview_dataset(
            db,
            dataset_id,
            project_id,
        )

    except ValueError:
        logger.exception(
            "Failed to preview dataset %s",
            dataset_id,
        )
        raise HTTPException(
            status_code=400,
            detail="Failed to read dataset",
        ) from None

    if preview is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    return preview


@router.get("/{dataset_id}/data")
async def get_dataset_data_endpoint(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _validate_workspace_project(
        db,
        workspace_id,
        project_id,
        current_user.id,
    )

    try:
        result = await get_dataset_data(
            db,
            dataset_id,
            project_id,
        )

    except ValueError:
        logger.exception(
            "Failed to read dataset %s",
            dataset_id,
        )
        raise HTTPException(
            status_code=400,
            detail="Failed to read dataset",
        ) from None

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    return result


@router.get("/{dataset_id}/columns")
async def get_dataset_columns_endpoint(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _validate_workspace_project(
        db,
        workspace_id,
        project_id,
        current_user.id,
    )

    await _validate_dataset_ownership(
        db,
        dataset_id,
        project_id,
    )

    columns = await get_dataset_columns(
        db,
        dataset_id,
    )

    if columns is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    return {
        "dataset_id": dataset_id,
        "columns": columns,
    }


@router.get("/{dataset_id}/profile")
async def get_dataset_profile_endpoint(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _validate_workspace_project(
        db,
        workspace_id,
        project_id,
        current_user.id,
    )

    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.project_id == project_id,
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    try:
        safe_path = _safe_dataset_file_path(
            dataset.file_path
        )
        df = pd.read_csv(safe_path)

    except Exception:
        logger.exception(
            "Failed to read dataset %s for profiling",
            dataset_id,
        )
        raise HTTPException(
            status_code=400,
            detail="Failed to read dataset file",
        ) from None

    try:
        profile = profile_dataset(df)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        logger.exception(
            "Failed to profile dataset %s",
            dataset_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to profile dataset",
        ) from None

    return {
        "dataset_id": dataset.id,
        "project_id": dataset.project_id,
        "name": dataset.name,
        "profile": profile,
    }


@router.get("/{dataset_id}/column-operations")
async def get_dataset_column_operations_endpoint(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _validate_workspace_project(
        db,
        workspace_id,
        project_id,
        current_user.id,
    )

    await _validate_dataset_ownership(
        db,
        dataset_id,
        project_id,
    )

    result = await get_dataset_column_operations(
        db,
        dataset_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    return {
        "dataset_id": dataset_id,
        "columns": result,
    }