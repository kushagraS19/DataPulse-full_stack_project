from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.database import get_db

from app.models.user_model import User

from app.schemas.chart_schema import (
    ChartCreate,
    ChartResponse
)

from app.services.chart_services import (
    create_chart,
    get_dashboard_charts,
    get_dashboard_by_id,
    get_chart_kpi,
    get_chart_line_data,
    get_chart_bar_data,
    get_chart_pie_data,
    get_chart_table_data,
    get_chart_data
)

from app.services.workspace_services import (
    get_workspace_by_id
)

from app.services.project_services import (
    get_project_by_id
)

from app.services.dataset_services import get_dataset_by_id, get_dataset_columns


router = APIRouter(
    prefix="/charts",
    tags=["Charts"]
)


@router.post(
    "/",
    response_model=ChartResponse
)
async def create_chart_endpoint(
    chart_data: ChartCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    workspace = await get_workspace_by_id(
        db,
        chart_data.workspace_id,
        current_user.id
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found"
        )

    project = await get_project_by_id(
        db,
        chart_data.project_id,
        chart_data.workspace_id
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    dashboard = await get_dashboard_by_id(
        db,
        chart_data.dashboard_id,
        chart_data.project_id
    )

    if dashboard is None:
        raise HTTPException(
            status_code=404,
            detail="Dashboard not found"
        )

    dataset = await get_dataset_by_id(
        db,
        chart_data.dataset_id,
        chart_data.project_id
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    if chart_data.column or chart_data.group_by:

        columns = await get_dataset_columns(
            db,
            chart_data.dataset_id
        )

        available_columns = {
            column["name"]
            for column in columns
        }

        if (
            chart_data.column
            and chart_data.column not in available_columns
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Column '{chart_data.column}' does not exist"
            )

        if (
            chart_data.group_by
            and chart_data.group_by not in available_columns
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Column '{chart_data.group_by}' does not exist"
            )

    if chart_data.operation:
        columns = await get_dataset_columns(
            db,
            chart_data.dataset_id
        )

        column_types = {
            column["name"]: column["data_type"]
            for column in columns
        }

        if chart_data.column:
            column_type = column_types.get(
                chart_data.column
            )

            numeric_operations = {
                "sum",
                "average",
                "min",
                "max"
            }

            if (
                chart_data.operation in numeric_operations
                and column_type not in {
                    "bigint",
                    "integer",
                    "smallint",
                    "numeric",
                    "double precision",
                    "real"
                }
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Operation '{chart_data.operation}' "
                        f"requires a numeric column"
                    )
                )

    allowed_chart_types = {
    "kpi",
    "line",
    "bar",
    "pie",
    "donut",
    "table"
    }

    if chart_data.chart_type not in allowed_chart_types:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported chart type: "
                f"{chart_data.chart_type}"
            )
        )

    allowed_operations = {
        "sum",
        "average",
        "count",
        "count_distinct",
        "min",
        "max"
    }

    if (
        chart_data.operation
        and chart_data.operation not in allowed_operations
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported operation: "
                f"{chart_data.operation}"
            )
        )

    if chart_data.operation in {
        "sum",
        "average",
        "min",
        "max",
        "count_distinct"
    } and not chart_data.column:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Operation '{chart_data.operation}' "
                f"requires a column"
            )
        )

    chart = await create_chart(
        db,
        chart_data.dashboard_id,
        chart_data.dataset_id,
        chart_data.name,
        chart_data.chart_type,
        chart_data.group_by,
        chart_data.operation,
        chart_data.column
    )

    return chart


@router.get(
    "/dashboard/{dashboard_id}",
    response_model=list[ChartResponse]
)
async def get_dashboard_charts_endpoint(
    dashboard_id: int,
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

    dashboard = await get_dashboard_by_id(
        db,
        dashboard_id,
        project_id
    )

    if dashboard is None:
        raise HTTPException(
            status_code=404,
            detail="Dashboard not found"
        )

    charts = await get_dashboard_charts(
        db,
        dashboard_id
    )

    return charts


@router.get(
    "/{chart_id}/kpi"
)
async def get_chart_kpi_endpoint(
    chart_id: int,
    dashboard_id: int,
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

    dashboard = await get_dashboard_by_id(
        db,
        dashboard_id,
        project_id
    )

    if dashboard is None:
        raise HTTPException(
            status_code=404,
            detail="Dashboard not found"
        )

    try:
        result = await get_chart_kpi(
            db,
            chart_id,
            dashboard_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Chart not found"
        )

    return result


@router.get(
    "/{chart_id}/line"
)
async def get_chart_line_endpoint(
    chart_id: int,
    dashboard_id: int,
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

    dashboard = await get_dashboard_by_id(
        db,
        dashboard_id,
        project_id
    )

    if dashboard is None:
        raise HTTPException(
            status_code=404,
            detail="Dashboard not found"
        )

    try:
        result = await get_chart_line_data(
            db,
            chart_id,
            dashboard_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Chart not found"
        )

    return result


@router.get(
    "/{chart_id}/bar"
)
async def get_chart_bar_endpoint(
    chart_id: int,
    dashboard_id: int,
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

    dashboard = await get_dashboard_by_id(
        db,
        dashboard_id,
        project_id
    )

    if dashboard is None:
        raise HTTPException(
            status_code=404,
            detail="Dashboard not found"
        )

    try:
        result = await get_chart_bar_data(
            db,
            chart_id,
            dashboard_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Chart not found"
        )

    return result


@router.get(
    "/{chart_id}/pie"
)
async def get_chart_pie_endpoint(
    chart_id: int,
    dashboard_id: int,
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

    dashboard = await get_dashboard_by_id(
        db,
        dashboard_id,
        project_id
    )

    if dashboard is None:
        raise HTTPException(
            status_code=404,
            detail="Dashboard not found"
        )

    try:
        result = await get_chart_pie_data(
            db,
            chart_id,
            dashboard_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Chart not found"
        )

    return result


@router.get(
    "/{chart_id}/table"
)
async def get_chart_table_endpoint(
    chart_id: int,
    dashboard_id: int,
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

    dashboard = await get_dashboard_by_id(
        db,
        dashboard_id,
        project_id
    )

    if dashboard is None:
        raise HTTPException(
            status_code=404,
            detail="Dashboard not found"
        )

    try:
        result = await get_chart_table_data(
            db,
            chart_id,
            dashboard_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Chart not found"
        )

    return result


@router.get("/{chart_id}/data")
async def get_chart_data_endpoint(
    chart_id: int,
    dashboard_id: int,
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

    dashboard = await get_dashboard_by_id(
        db,
        dashboard_id,
        project_id
    )

    if dashboard is None:
        raise HTTPException(
            status_code=404,
            detail="Dashboard not found"
        )

    result = await get_chart_data(
        db,
        chart_id,
        dashboard_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Chart not found"
        )

    return result


