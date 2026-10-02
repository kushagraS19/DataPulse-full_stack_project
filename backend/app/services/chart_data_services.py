from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


ALLOWED_OPERATIONS = {
    "sum": "SUM",
    "average": "AVG",
    "count": "COUNT",
    "count_distinct": "COUNT(DISTINCT",
    "min": "MIN",
    "max": "MAX"
}


async def get_chart_data(
    db: AsyncSession,
    chart_type: str,
    table_name: str,
    group_by: str | None = None,
    operation: str | None = None,
    column: str | None = None,
    x_column: str | None = None,
    y_column: str | None = None
):
    if chart_type == "scatter":
        return await get_scatter_chart_data(
            db=db,
            table_name=table_name,
            x_column=x_column,
            y_column=y_column
        )

    if chart_type in {"bar", "pie", "line"}:
        return await get_grouped_chart_data(
            db=db,
            table_name=table_name,
            group_by=group_by,
            operation=operation,
            column=column
        )

    return []


async def get_grouped_chart_data(
    db: AsyncSession,
    table_name: str,
    group_by: str | None,
    operation: str | None,
    column: str | None
):
    if not group_by:
        return []

    if not operation:
        return []

    if operation not in ALLOWED_OPERATIONS:
        return []

    if operation == "count":
        aggregate_sql = "COUNT(*) AS value"

    elif operation == "count_distinct":
        if not column:
            return []

        aggregate_sql = (
            f'COUNT(DISTINCT "{column}") AS value'
        )

    else:
        if not column:
            return []

        sql_operation = ALLOWED_OPERATIONS[operation]

        aggregate_sql = (
            f'{sql_operation}("{column}") AS value'
        )

    query = text(
        f"""
        SELECT
            "{group_by}" AS "{group_by}",
            {aggregate_sql}
        FROM "{table_name}"
        GROUP BY "{group_by}"
        ORDER BY value DESC
        """
    )

    result = await db.execute(query)

    rows = result.mappings().all()

    return [
        dict(row)
        for row in rows
    ]


async def get_scatter_chart_data(
    db: AsyncSession,
    table_name: str,
    x_column: str | None,
    y_column: str | None
):
    if not x_column or not y_column:
        return []

    query = text(
        f"""
        SELECT
            "{x_column}" AS "{x_column}",
            "{y_column}" AS "{y_column}"
        FROM "{table_name}"
        WHERE
            "{x_column}" IS NOT NULL
            AND "{y_column}" IS NOT NULL
        """
    )

    result = await db.execute(query)

    rows = result.mappings().all()

    return [
        dict(row)
        for row in rows
    ]


