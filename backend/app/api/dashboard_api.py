from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.database import get_db

from app.models.user_model import User

from app.schemas.dashboard_schema import (
    DashboardCreate,
    DashboardResponse
)

from app.services.chart_services import get_dashboard_by_id, create_chart, delete_dashboard_charts

from app.services.dashboard_services import (
    create_dashboard,
    get_project_dashboards
)

from app.services.workspace_services import (
    get_workspace_by_id
)

from app.services.project_services import (
    get_project_by_id
)

from app.services.dashboard_generator_services import (
    generate_dashboard_config
)

router = APIRouter(
    prefix="/dashboards",
    tags=["Dashboards"]
)


@router.post(
    "/",
    response_model=DashboardResponse
)
async def create_dashboard_endpoint(
    dashboard_data: DashboardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    workspace = await get_workspace_by_id(
        db,
        dashboard_data.workspace_id,
        current_user.id
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found"
        )

    project = await get_project_by_id(
        db,
        dashboard_data.project_id,
        dashboard_data.workspace_id
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    dashboard = await create_dashboard(
        db,
        dashboard_data.project_id,
        dashboard_data.name
    )

    return dashboard

@router.get(
    "/project/{project_id}",
    response_model=list[DashboardResponse]
)
async def get_project_dashboards_endpoint(
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

    dashboards = await get_project_dashboards(
        db,
        project_id
    )

    return dashboards


@router.get("/{dashboard_id}/generate")
async def generate_dashboard_endpoint(
    dashboard_id: int,
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

    result = await generate_dashboard_config(
        db,
        dataset_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    await delete_dashboard_charts(
        db,
        dashboard_id
    )

    generated_charts = []

    for chart_config in result["charts"]:

        chart = await create_chart(
            db=db,
            dashboard_id=dashboard_id,
            dataset_id=dataset_id,
            name=chart_config["name"],
            chart_type=chart_config["chart_type"],
            group_by=chart_config.get("group_by"),
            operation=chart_config.get("operation"),
            column=chart_config.get("column"),
            x_column=chart_config.get("x_column"),
            y_column=chart_config.get("y_column")
        )

        generated_charts.append({
            "id": chart.id,
            "name": chart.name,
            "chart_type": chart.chart_type,
            "group_by": chart.group_by,
            "operation": chart.operation,
            "column": chart.column,
            "x_column": chart.x_column,
            "y_column": chart.y_column
        })

    return {
        "dashboard_id": dashboard_id,
        "dataset_id": dataset_id,
        "kpis": result["kpis"],
        "charts": generated_charts,
        "insights": result["insights"],
        "detected_columns": result["detected_columns"]
    }