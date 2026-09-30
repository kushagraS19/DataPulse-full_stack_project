from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.ext.asyncio import AsyncSession
from app.services.project_services import get_project_by_id
from app.services.workspace_services import get_workspace_by_id
from app.services.dataset_services import get_dataset_by_id
from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user_model import User
from app.services.analytics_services import calculate_sum, calculate_average, calculate_count, calculate_count_distinct, calculate_max, calculate_min, group_by_column, filter_dataset, sort_dataset, aggregate_by_date, calculate_kpi, run_chart_query
from fastapi import APIRouter

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get(
    "/{dataset_id}/sum"
)
async def get_dataset_sum(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    column: str,
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

    dataset = await get_dataset_by_id(
        db,
        dataset_id,
        project_id
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:
        result = await calculate_sum(
            db,
            dataset_id,
            column
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {
        "dataset_id": dataset_id,
        "column": column,
        "operation": "sum",
        "value": result
    }



@router.get(
    "/{dataset_id}/avg"
)
async def get_dataset_average(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    column: str,
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

    dataset = await get_dataset_by_id(
        db,
        dataset_id,
        project_id
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:
        result = await calculate_average(
            db,
            dataset_id,
            column
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {
        "dataset_id": dataset_id,
        "column": column,
        "operation": "average",
        "value": result
    }



@router.get(
    "/{dataset_id}/count"
)
async def get_dataset_count(
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

    dataset = await get_dataset_by_id(
        db,
        dataset_id,
        project_id
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:
        result = await calculate_count(
            db,
            dataset_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {
        "dataset_id": dataset_id,
        "operation": "count",
        "value": result
    }


@router.get(
    "/{dataset_id}/count-distinct"
)
async def get_count_distinct(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    column: str,
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

    dataset = await get_dataset_by_id(
        db,
        dataset_id,
        project_id
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:
        result = await calculate_count_distinct(
            db,
            dataset_id,
            column
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {
        "dataset_id": dataset_id,
        "column": column,
        "operation": "count_distinct",
        "value": result
    }


@router.get(
    "/{dataset_id}/min"
)
async def get_dataset_min(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    column: str,
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

    dataset = await get_dataset_by_id(
        db,
        dataset_id,
        project_id
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:
        result = await calculate_min(
            db,
            dataset_id,
            column
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {
        "dataset_id": dataset_id,
        "column": column,
        "operation": "min",
        "value": result
    }


@router.get(
    "/{dataset_id}/max"
)
async def get_dataset_max(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    column: str,
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

    dataset = await get_dataset_by_id(
        db,
        dataset_id,
        project_id
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:
        result = await calculate_max(
            db,
            dataset_id,
            column
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {
        "dataset_id": dataset_id,
        "column": column,
        "operation": "max",
        "value": result
    }


@router.get(
    "/{dataset_id}/group-by"
)
async def get_grouped_data(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    column: str,
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

    dataset = await get_dataset_by_id(
        db,
        dataset_id,
        project_id
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:
        result = await group_by_column(
            db,
            dataset_id,
            column
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {
        "dataset_id": dataset_id,
        "column": column,
        "operation": "group_by",
        "data": result
    }


@router.get(
    "/{dataset_id}/filter"
)
async def get_filtered_data(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    column: str,
    value: str,
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

    dataset = await get_dataset_by_id(
        db,
        dataset_id,
        project_id
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:
        result = await filter_dataset(
            db,
            dataset_id,
            column,
            value
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {
        "dataset_id": dataset_id,
        "column": column,
        "value": value,
        "operation": "filter",
        "data": result
    }


@router.get(
    "/{dataset_id}/sort"
)
async def get_sorted_data(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    column: str,
    order: str = "asc",
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

    dataset = await get_dataset_by_id(
        db,
        dataset_id,
        project_id
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:
        result = await sort_dataset(
            db,
            dataset_id,
            column,
            order
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {
        "dataset_id": dataset_id,
        "column": column,
        "order": order,
        "operation": "sort",
        "data": result
    }


@router.get(
    "/{dataset_id}/date-aggregation"
)
async def get_date_aggregation(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    date_column: str,
    period: str,
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

    dataset = await get_dataset_by_id(
        db,
        dataset_id,
        project_id
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:
        result = await aggregate_by_date(
            db,
            dataset_id,
            date_column,
            period
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {
        "dataset_id": dataset_id,
        "date_column": date_column,
        "period": period,
        "operation": "date_aggregation",
        "data": result
    }


@router.get(
    "/{dataset_id}/kpi"
)
async def get_kpi(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    operation: str,
    column: str | None = None,
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

    dataset = await get_dataset_by_id(
        db,
        dataset_id,
        project_id
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:
        result = await calculate_kpi(
            db,
            dataset_id,
            operation,
            column
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {
        "dataset_id": dataset_id,
        "operation": operation,
        "column": column,
        "value": result
    }


@router.get(
    "/{dataset_id}/chart"
)
async def get_chart_data(
    dataset_id: int,
    project_id: int,
    workspace_id: int,
    group_by: str,
    operation: str,
    column: str | None = None,
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

    dataset = await get_dataset_by_id(
        db,
        dataset_id,
        project_id
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    try:
        result = await run_chart_query(
            db,
            dataset_id,
            group_by,
            operation,
            column
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {
        "dataset_id": dataset_id,
        "group_by": group_by,
        "operation": operation,
        "column": column,
        "data": result
    }


