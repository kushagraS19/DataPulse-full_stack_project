from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_model import Dataset


async def get_date_column_profile(
    db: AsyncSession,
    dataset_id: int,
    date_column: str
):
    dataset_result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = dataset_result.scalar_one_or_none()

    if dataset is None:
        return None

    query = text(
        f'''
        SELECT
            MIN("{date_column}") AS min_date,
            MAX("{date_column}") AS max_date,
            COUNT("{date_column}") AS non_null_count,
            COUNT(DISTINCT "{date_column}") AS unique_dates
        FROM "{dataset.table_name}"
        '''
    )

    result = await db.execute(query)

    row = result.fetchone()

    if row is None:
        return None

    min_date = row.min_date
    max_date = row.max_date

    date_range_days = None

    if min_date is not None and max_date is not None:
        date_range_days = (
            max_date - min_date
        ).days

    return {
        "column": date_column,
        "min_date": min_date,
        "max_date": max_date,
        "non_null_count": row.non_null_count,
        "unique_dates": row.unique_dates,
        "date_range_days": date_range_days
    }


def determine_date_granularity(
    date_profile: dict
):
    date_range_days = date_profile.get(
        "date_range_days"
    )

    unique_dates = date_profile.get(
        "unique_dates",
        0
    )

    if date_range_days is None:
        return None

    if date_range_days <= 31:
        return "day"

    if date_range_days <= 180:

        if unique_dates >= 20:
            return "week"

        return "month"

    if date_range_days <= 730:
        return "month"

    return "year"


async def analyze_date_columns(
    db: AsyncSession,
    dataset_id: int,
    date_columns: list[str]
):
    date_profiles = []

    for date_column in date_columns:

        profile = await get_date_column_profile(
            db,
            dataset_id,
            date_column
        )

        if profile is None:
            continue

        profile["granularity"] = (
            determine_date_granularity(
                profile
            )
        )

        date_profiles.append(
            profile
        )

    return date_profiles