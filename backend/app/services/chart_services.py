from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chart_model import Chart
from app.models.dashboard_model import Dashboard
from app.services.analytics_services import calculate_kpi
from app.services.analytics_services import aggregate_by_date, run_chart_query

import pandas as pd

from app.models.dataset_model import Dataset


async def create_chart(
    db: AsyncSession,
    dashboard_id: int,
    dataset_id:int,
    name: str,
    chart_type: str,
    group_by: str | None,
    operation: str | None,
    column: str | None
):
    chart = Chart(
        name=name,
        chart_type=chart_type,
        dashboard_id=dashboard_id,
        dataset_id=dataset_id,
        group_by=group_by,
        operation=operation,
        column=column
    )

    db.add(chart)

    await db.flush()
    await db.refresh(chart)
    await db.commit()

    return chart


async def get_dashboard_charts(
    db: AsyncSession,
    dashboard_id: int
):
    result = await db.execute(
        select(Chart).where(
            Chart.dashboard_id == dashboard_id
        )
    )

    return result.scalars().all()


async def get_dashboard_by_id(
    db: AsyncSession,
    dashboard_id: int,
    project_id: int
):
    result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.project_id == project_id
        )
    )

    return result.scalar_one_or_none()


async def get_chart_kpi(
    db: AsyncSession,
    chart_id: int,
    dashboard_id: int
):
    result = await db.execute(
        select(Chart).where(
            Chart.id == chart_id,
            Chart.dashboard_id == dashboard_id
        )
    )

    chart = result.scalar_one_or_none()

    if chart is None:
        return None

    if chart.operation is None:
        raise ValueError(
            "Chart operation is required"
        )

    if chart.operation != "count" and chart.column is None:
        raise ValueError(
            "Chart column is required"
        )

    value = await calculate_kpi(
        db,
        chart.dataset_id,
        chart.operation,
        chart.column
    )

    return {
        "chart_id": chart.id,
        "name": chart.name,
        "chart_type": chart.chart_type,
        "operation": chart.operation,
        "column": chart.column,
        "value": value
    }


async def get_chart_line_data(
    db: AsyncSession,
    chart_id: int,
    dashboard_id: int
):
    result = await db.execute(
        select(Chart).where(
            Chart.id == chart_id,
            Chart.dashboard_id == dashboard_id
        )
    )

    chart = result.scalar_one_or_none()

    if chart is None:
        return None

    if chart.operation is None:
        raise ValueError(
            "Chart operation is required"
        )

    if chart.column is None:
        raise ValueError(
            "Chart column is required"
        )

    if chart.group_by is None:
        raise ValueError(
            "Date column is required"
        )

    data = await aggregate_by_date(
        db,
        chart.dataset_id,
        chart.group_by,
        "month"
    )

    return {
        "chart_id": chart.id,
        "name": chart.name,
        "chart_type": chart.chart_type,
        "operation": chart.operation,
        "column": chart.column,
        "date_column": chart.group_by,
        "data": data
    }


async def get_chart_bar_data(
    db: AsyncSession,
    chart_id: int,
    dashboard_id: int
):
    result = await db.execute(
        select(Chart).where(
            Chart.id == chart_id,
            Chart.dashboard_id == dashboard_id
        )
    )

    chart = result.scalar_one_or_none()

    if chart is None:
        return None

    if chart.operation is None:
        raise ValueError(
            "Chart operation is required"
        )

    if chart.group_by is None:
        raise ValueError(
            "Group by column is required"
        )

    if chart.operation != "count" and chart.column is None:
        raise ValueError(
            "Chart column is required"
        )

    data = await run_chart_query(
        db,
        chart.dataset_id,
        chart.group_by,
        chart.operation,
        chart.column
    )

    return {
        "chart_id": chart.id,
        "name": chart.name,
        "chart_type": chart.chart_type,
        "operation": chart.operation,
        "column": chart.column,
        "group_by": chart.group_by,
        "data": data
    }


async def get_chart_pie_data(
    db: AsyncSession,
    chart_id: int,
    dashboard_id: int
):
    result = await db.execute(
        select(Chart).where(
            Chart.id == chart_id,
            Chart.dashboard_id == dashboard_id
        )
    )

    chart = result.scalar_one_or_none()

    if chart is None:
        return None

    if chart.operation is None:
        raise ValueError(
            "Chart operation is required"
        )

    if chart.group_by is None:
        raise ValueError(
            "Group by column is required"
        )

    if chart.operation != "count" and chart.column is None:
        raise ValueError(
            "Chart column is required"
        )

    data = await run_chart_query(
        db,
        chart.dataset_id,
        chart.group_by,
        chart.operation,
        chart.column
    )

    return {
        "chart_id": chart.id,
        "name": chart.name,
        "chart_type": chart.chart_type,
        "operation": chart.operation,
        "column": chart.column,
        "group_by": chart.group_by,
        "data": data
    }


async def get_chart_table_data(
    db: AsyncSession,
    chart_id: int,
    dashboard_id: int
):
    result = await db.execute(
        select(Chart).where(
            Chart.id == chart_id,
            Chart.dashboard_id == dashboard_id
        )
    )

    chart = result.scalar_one_or_none()

    if chart is None:
        return None

    dataset = await db.execute(
        select(Dataset).where(
            Dataset.id == chart.dataset_id
        )
    )

    dataset = dataset.scalar_one_or_none()

    if dataset is None:
        raise ValueError(
            "Dataset not found"
        )

    try:
        df = pd.read_csv(
            dataset.file_path
        )

    except Exception as e:
        raise ValueError(
            f"Failed to read dataset: {str(e)}"
        )

    data = df.to_dict(
        orient="records"
    )

    return {
        "chart_id": chart.id,
        "name": chart.name,
        "chart_type": chart.chart_type,
        "columns": list(df.columns),
        "data": data
    }


async def get_chart_data(
    db: AsyncSession,
    chart_id: int,
    dashboard_id: int
):
    result = await db.execute(
        select(Chart).where(
            Chart.id == chart_id,
            Chart.dashboard_id == dashboard_id
        )
    )

    chart = result.scalar_one_or_none()

    if chart is None:
        return None

    data = await run_chart_query(
        db=db,
        dataset_id=chart.dataset_id,
        group_by=chart.group_by,
        operation=chart.operation,
        column=chart.column
    )

    return {
        "chart_id": chart.id,
        "name": chart.name,
        "chart_type": chart.chart_type,
        "configuration": {
            "dataset_id": chart.dataset_id,
            "group_by": chart.group_by,
            "operation": chart.operation,
            "column": chart.column
        },
        "data": data
    }


    