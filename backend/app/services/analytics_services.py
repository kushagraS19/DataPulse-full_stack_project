import pandas as pd

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_model import Dataset



async def calculate_sum(
    db: AsyncSession,
    dataset_id: int,
    column: str 
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    try:
        df = pd.read_csv(
            dataset.file_path
        )
    except Exception as e:
        raise ValueError(
            f"Failed to read dataset: {str(e)}"
        )

    if column not in df.columns:
        raise ValueError(
            f"Column '{column}' not found"
        )

    if not pd.api.types.is_numeric_dtype(
        df[column]
    ):
        raise ValueError(
            f"Column '{column}' must be numeric"
        )

    return df[column].sum()


async def calculate_average(
    db: AsyncSession,
    dataset_id: int,
    column: str
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    try:
        df = pd.read_csv(
            dataset.file_path
        )
    except Exception as e:
        raise ValueError(
            f"Failed to read dataset: {str(e)}"
        )

    if column not in df.columns:
        raise ValueError(
            f"Column '{column}' not found"
        )

    if not pd.api.types.is_numeric_dtype(
        df[column]
    ):
        raise ValueError(
            f"Column '{column}' must be numeric"
        )

    return df[column].mean()


async def calculate_count(
    db: AsyncSession,
    dataset_id: int
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    try:
        df = pd.read_csv(
            dataset.file_path
        )
    except Exception as e:
        raise ValueError(
            f"Failed to read dataset: {str(e)}"
        )

    return len(df)


async def calculate_count_distinct(
    db: AsyncSession,
    dataset_id: int,
    column: str
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    try:
        df = pd.read_csv(
            dataset.file_path
        )
    except Exception as e:
        raise ValueError(
            f"Failed to read dataset: {str(e)}"
        )

    if column not in df.columns:
        raise ValueError(
            f"Column '{column}' not found"
        )

    return df[column].nunique()


async def calculate_min(
    db: AsyncSession,
    dataset_id: int,
    column: str
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    try:
        df = pd.read_csv(
            dataset.file_path
        )
    except Exception as e:
        raise ValueError(
            f"Failed to read dataset: {str(e)}"
        )

    if column not in df.columns:
        raise ValueError(
            f"Column '{column}' not found"
        )

    if not pd.api.types.is_numeric_dtype(
        df[column]
    ):
        raise ValueError(
            f"Column '{column}' must be numeric"
        )

    return df[column].min()


async def calculate_max(
    db: AsyncSession,
    dataset_id: int,
    column: str
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    try:
        df = pd.read_csv(
            dataset.file_path
        )
    except Exception as e:
        raise ValueError(
            f"Failed to read dataset: {str(e)}"
        )

    if column not in df.columns:
        raise ValueError(
            f"Column '{column}' not found"
        )

    if not pd.api.types.is_numeric_dtype(
        df[column]
    ):
        raise ValueError(
            f"Column '{column}' must be numeric"
        )

    return df[column].max()


async def group_by_column(
    db: AsyncSession,
    dataset_id: int,
    column: str
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    try:
        df = pd.read_csv(
            dataset.file_path
        )
    except Exception as e:
        raise ValueError(
            f"Failed to read dataset: {str(e)}"
        )

    if column not in df.columns:
        raise ValueError(
            f"Column '{column}' not found"
        )

    grouped_data = (
        df.groupby(
            column,
            dropna=False
        )
        .size()
        .reset_index(
            name="count"
        )
    )

    return grouped_data.to_dict(
        orient="records"
    )

async def filter_dataset(
    db: AsyncSession,
    dataset_id: int,
    column: str,
    value: str
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    try:
        df = pd.read_csv(
            dataset.file_path
        )
    except Exception as e:
        raise ValueError(
            f"Failed to read dataset: {str(e)}"
        )

    if column not in df.columns:
        raise ValueError(
            f"Column '{column}' not found"
        )

    filtered_data = df[
        df[column].astype(str) == value
    ]

    return filtered_data.to_dict(
        orient="records"
    )


async def sort_dataset(
    db: AsyncSession,
    dataset_id: int,
    column: str,
    order: str
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    try:
        df = pd.read_csv(
            dataset.file_path
        )
    except Exception as e:
        raise ValueError(
            f"Failed to read dataset: {str(e)}"
        )

    if column not in df.columns:
        raise ValueError(
            f"Column '{column}' not found"
        )

    if order not in ["asc", "desc"]:
        raise ValueError(
            "Order must be 'asc' or 'desc'"
        )

    sorted_data = df.sort_values(
        by=column,
        ascending=(order == "asc")
    )

    return sorted_data.to_dict(
        orient="records"
    )


async def aggregate_by_date(
    db: AsyncSession,
    dataset_id: int,
    date_column: str,
    period: str
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    try:
        df = pd.read_csv(
            dataset.file_path
        )
    except Exception as e:
        raise ValueError(
            f"Failed to read dataset: {str(e)}"
        )

    if date_column not in df.columns:
        raise ValueError(
            f"Column '{date_column}' not found"
        )

    if period not in ["day", "week", "month", "year"]:
        raise ValueError(
            "Period must be day, week, month, or year"
        )

    df[date_column] = pd.to_datetime(
        df[date_column],
        errors="coerce"
    )

    if df[date_column].isna().all():
        raise ValueError(
            f"Column '{date_column}' does not contain valid dates"
        )

    if period == "day":
        df["period"] = df[date_column].dt.strftime(
            "%Y-%m-%d"
        )

    elif period == "week":
        df["period"] = (
            df[date_column]
            .dt.to_period("W")
            .astype(str)
        )

    elif period == "month":
        df["period"] = df[date_column].dt.strftime(
            "%Y-%m"
        )

    else:
        df["period"] = df[date_column].dt.strftime(
            "%Y"
        )

    aggregated_data = (
        df.groupby("period")
        .size()
        .reset_index(
            name="count"
        )
    )

    return aggregated_data.to_dict(
        orient="records"
    )


async def calculate_kpi(
    db: AsyncSession,
    dataset_id: int,
    operation: str,
    column: str | None = None
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    try:
        df = pd.read_csv(
            dataset.file_path
        )
    except Exception as e:
        raise ValueError(
            f"Failed to read dataset: {str(e)}"
        )

    allowed_operations = [
        "sum",
        "average",
        "count",
        "count_distinct",
        "min",
        "max"
    ]

    if operation not in allowed_operations:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )

    if operation == "count":
        return len(df)

    if column is None:
        raise ValueError(
            "Column is required for this operation"
        )

    if column not in df.columns:
        raise ValueError(
            f"Column '{column}' not found"
        )

    if operation == "count_distinct":
        return df[column].nunique()

    if not pd.api.types.is_numeric_dtype(
        df[column]
    ):
        raise ValueError(
            f"Column '{column}' must be numeric"
        )

    if operation == "sum":
        return df[column].sum()

    if operation == "average":
        return df[column].mean()

    if operation == "min":
        return df[column].min()

    if operation == "max":
        return df[column].max()


async def run_chart_query(
    db: AsyncSession,
    dataset_id: int,
    group_by: str,
    operation: str,
    column: str | None = None
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    try:
        df = pd.read_csv(
            dataset.file_path
        )
    except Exception as e:
        raise ValueError(
            f"Failed to read dataset: {str(e)}"
        )

    if group_by not in df.columns:
        raise ValueError(
            f"Group-by column '{group_by}' not found"
        )

    allowed_operations = [
        "sum",
        "average",
        "count",
        "count_distinct",
        "min",
        "max"
    ]

    if operation not in allowed_operations:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )

    if operation == "count":
        grouped_data = (
            df.groupby(group_by, dropna=False)
            .size()
            .reset_index(name="value")
        )

        return grouped_data.to_dict(
            orient="records"
        )

    if column is None:
        raise ValueError(
            "Column is required for this operation"
        )

    if column not in df.columns:
        raise ValueError(
            f"Column '{column}' not found"
        )

    if operation == "count_distinct":
        grouped_data = (
            df.groupby(group_by, dropna=False)[column]
            .nunique()
            .reset_index(name="value")
        )

    else:
        if not pd.api.types.is_numeric_dtype(
            df[column]
        ):
            raise ValueError(
                f"Column '{column}' must be numeric"
            )

        if operation == "sum":
            grouped_data = (
                df.groupby(group_by, dropna=False)[column]
                .sum()
                .reset_index(name="value")
            )

        elif operation == "average":
            grouped_data = (
                df.groupby(group_by, dropna=False)[column]
                .mean()
                .reset_index(name="value")
            )

        elif operation == "min":
            grouped_data = (
                df.groupby(group_by, dropna=False)[column]
                .min()
                .reset_index(name="value")
            )

        elif operation == "max":
            grouped_data = (
                df.groupby(group_by, dropna=False)[column]
                .max()
                .reset_index(name="value")
            )

    return grouped_data.to_dict(
        orient="records"
    )