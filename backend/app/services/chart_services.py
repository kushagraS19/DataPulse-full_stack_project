from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

import pandas as pd

from app.models.chart_model import Chart
from app.models.dashboard_model import Dashboard
from app.models.dataset_model import Dataset
from app.services.analytics_services import calculate_kpi, aggregate_by_date, run_chart_query


def _quote_identifier(identifier: str) -> str:
    """Quote a PostgreSQL identifier safely."""
    return '"' + identifier.replace('"', '""') + '"'


async def create_chart(
    db: AsyncSession,
    dashboard_id: int,
    dataset_id: int,
    name: str,
    chart_type: str,
    group_by: str | None,
    operation: str | None,
    column: str | None,
    x_column: str | None = None,
    y_column: str | None = None,
):
    chart = Chart(
        name=name,
        chart_type=chart_type,
        dashboard_id=dashboard_id,
        dataset_id=dataset_id,
        group_by=group_by,
        operation=operation,
        column=column,
        x_column=x_column,
        y_column=y_column,
    )
    db.add(chart)
    await db.flush()
    await db.refresh(chart)
    await db.commit()
    return chart


async def get_dashboard_charts(db: AsyncSession, dashboard_id: int):
    result = await db.execute(
        select(Chart).where(Chart.dashboard_id == dashboard_id)
    )
    return result.scalars().all()


async def get_dashboard_by_id(db: AsyncSession, dashboard_id: int, project_id: int):
    result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.project_id == project_id,
        )
    )
    return result.scalar_one_or_none()


async def get_chart_kpi(db: AsyncSession, chart_id: int, dashboard_id: int):
    result = await db.execute(
        select(Chart).where(
            Chart.id == chart_id,
            Chart.dashboard_id == dashboard_id,
        )
    )
    chart = result.scalar_one_or_none()
    if chart is None:
        return None
    if chart.operation is None:
        raise ValueError("Chart operation is required")
    if chart.operation != "count" and chart.column is None:
        raise ValueError("Chart column is required")

    value = await calculate_kpi(db, chart.dataset_id, chart.operation, chart.column)
    return {
        "chart_id": chart.id,
        "name": chart.name,
        "chart_type": chart.chart_type,
        "operation": chart.operation,
        "column": chart.column,
        "value": value,
    }


async def get_chart_line_data(db: AsyncSession, chart_id: int, dashboard_id: int):
    result = await db.execute(
        select(Chart).where(
            Chart.id == chart_id,
            Chart.dashboard_id == dashboard_id,
        )
    )
    chart = result.scalar_one_or_none()
    if chart is None:
        return None
    if chart.operation is None:
        raise ValueError("Chart operation is required")
    if chart.column is None:
        raise ValueError("Chart column is required")
    if chart.group_by is None:
        raise ValueError("Date column is required")

    data = await aggregate_by_date(db, chart.dataset_id, chart.group_by, "month")
    return {
        "chart_id": chart.id,
        "name": chart.name,
        "chart_type": chart.chart_type,
        "operation": chart.operation,
        "column": chart.column,
        "date_column": chart.group_by,
        "data": data,
    }


async def get_chart_bar_data(db: AsyncSession, chart_id: int, dashboard_id: int):
    result = await db.execute(
        select(Chart).where(
            Chart.id == chart_id,
            Chart.dashboard_id == dashboard_id,
        )
    )
    chart = result.scalar_one_or_none()
    if chart is None:
        return None
    if chart.operation is None:
        raise ValueError("Chart operation is required")
    if chart.group_by is None:
        raise ValueError("Group by column is required")
    if chart.operation != "count" and chart.column is None:
        raise ValueError("Chart column is required")

    data = await run_chart_query(
        db, chart.dataset_id, chart.group_by, chart.operation, chart.column
    )
    return {
        "chart_id": chart.id,
        "name": chart.name,
        "chart_type": chart.chart_type,
        "operation": chart.operation,
        "column": chart.column,
        "group_by": chart.group_by,
        "data": data,
    }


async def get_chart_pie_data(db: AsyncSession, chart_id: int, dashboard_id: int):
    result = await db.execute(
        select(Chart).where(
            Chart.id == chart_id,
            Chart.dashboard_id == dashboard_id,
        )
    )
    chart = result.scalar_one_or_none()
    if chart is None:
        return None
    if chart.operation is None:
        raise ValueError("Chart operation is required")
    if chart.group_by is None:
        raise ValueError("Group by column is required")
    if chart.operation != "count" and chart.column is None:
        raise ValueError("Chart column is required")

    data = await run_chart_query(
        db, chart.dataset_id, chart.group_by, chart.operation, chart.column
    )
    return {
        "chart_id": chart.id,
        "name": chart.name,
        "chart_type": chart.chart_type,
        "operation": chart.operation,
        "column": chart.column,
        "group_by": chart.group_by,
        "data": data,
    }


async def get_chart_table_data(db: AsyncSession, chart_id: int, dashboard_id: int):
    result = await db.execute(
        select(Chart).where(
            Chart.id == chart_id,
            Chart.dashboard_id == dashboard_id,
        )
    )
    chart = result.scalar_one_or_none()
    if chart is None:
        return None

    dataset_result = await db.execute(
        select(Dataset).where(Dataset.id == chart.dataset_id)
    )
    dataset = dataset_result.scalar_one_or_none()
    if dataset is None:
        raise ValueError("Dataset not found")

    try:
        df = pd.read_csv(dataset.file_path)
    except Exception as exc:
        raise ValueError(f"Failed to read dataset: {exc}") from exc

    return {
        "chart_id": chart.id,
        "name": chart.name,
        "chart_type": chart.chart_type,
        "columns": list(df.columns),
        "data": df.to_dict(orient="records"),
    }


async def _get_raw_numeric_values(
    db: AsyncSession,
    table_name: str,
    column: str,
) -> list[dict]:
    query = text(
        f"""
        SELECT CAST({_quote_identifier(column)} AS DOUBLE PRECISION) AS value
        FROM {_quote_identifier(table_name)}
        WHERE {_quote_identifier(column)} IS NOT NULL
        """
    )
    result = await db.execute(query)
    return [
        {"value": row["value"]}
        for row in result.mappings().all()
        if row["value"] is not None
    ]


async def _get_numeric_pairs(
    db: AsyncSession,
    table_name: str,
    x_column: str,
    y_column: str,
) -> list[dict]:
    x = _quote_identifier(x_column)
    y = _quote_identifier(y_column)
    query = text(
        f"""
        SELECT CAST({x} AS DOUBLE PRECISION) AS {x},
               CAST({y} AS DOUBLE PRECISION) AS {y}
        FROM {_quote_identifier(table_name)}
        WHERE {x} IS NOT NULL AND {y} IS NOT NULL
        """
    )
    result = await db.execute(query)
    return [dict(row) for row in result.mappings().all()]


async def get_chart_data(
    db: AsyncSession,
    chart_id: int,
    dashboard_id: int,
    chart_type: str,
    dataset_id: int,
    table_name: str,
    group_by: str | None,
    operation: str | None,
    column: str | None,
    x_column: str | None = None,
    y_column: str | None = None,
):
    result = await db.execute(
        select(Chart).where(
            Chart.id == chart_id,
            Chart.dashboard_id == dashboard_id,
        )
    )
    chart = result.scalar_one_or_none()
    if chart is None:
        return None

    if chart_type in {"histogram", "boxplot"}:
        if not column:
            raise ValueError(f"{chart_type} requires a numeric column")
        data = await _get_raw_numeric_values(db, table_name, column)
    elif chart_type in {"scatter", "heatmap"}:
        if not x_column or not y_column:
            raise ValueError(f"{chart_type} requires x_column and y_column")
        data = await _get_numeric_pairs(db, table_name, x_column, y_column)
    else:
        if not group_by:
            raise ValueError(f"{chart_type} requires a group_by column")
        if not operation:
            raise ValueError(f"{chart_type} requires an operation")
        data = await run_chart_query(
            db=db,
            dataset_id=dataset_id,
            group_by=group_by,
            operation=operation,
            column=column,
        )

    return {
        "chart_id": chart.id,
        "name": chart.name,
        "chart_type": chart.chart_type,
        "configuration": {
            "dataset_id": dataset_id,
            "table_name": table_name,
            "group_by": group_by,
            "operation": operation,
            "column": column,
            "x_column": x_column,
            "y_column": y_column,
        },
        "data": data,
    }


async def delete_dashboard_charts(db: AsyncSession, dashboard_id: int):
    result = await db.execute(
        select(Chart).where(Chart.dashboard_id == dashboard_id)
    )
    charts = result.scalars().all()
    for chart in charts:
        await db.delete(chart)
    await db.flush()
