# ============================================================
# IMPORTS
# ============================================================

import pandas as pd

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.dataset_model import Dataset
from app.models.project_model import Project
from app.models.user_model import User
from app.services.insight_services import (
    generate_dataset_insights,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/insights",
    tags=["Insights"],
)


# ============================================================
# GET DATASET INSIGHTS
# ============================================================

@router.get(
    "/dataset/{dataset_id}"
)
async def get_dataset_insights(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    # --------------------------------------------------------
    # Verify project
    # --------------------------------------------------------

    project_result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.workspace_id == workspace_id
        )
    )

    project = (
        project_result
        .scalar_one_or_none()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # --------------------------------------------------------
    # Verify dataset
    # --------------------------------------------------------

    dataset_result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.project_id == project_id
        )
    )

    dataset = (
        dataset_result
        .scalar_one_or_none()
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    # --------------------------------------------------------
    # Read dataset
    # --------------------------------------------------------

    try:

        df = pd.read_csv(
            dataset.file_path
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to read dataset: {str(e)}"
            )
        )

    # --------------------------------------------------------
    # Generate insights
    # --------------------------------------------------------

    try:

        result = generate_dataset_insights(
            df
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to generate insights: {str(e)}"
            )
        )

    return {
        "dataset_id": dataset.id,
        "project_id": dataset.project_id,
        "dataset_name": dataset.name,
        **result,
    }