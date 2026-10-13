from datetime import date, datetime
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_model import Dataset


def parse_date(value):
    """Convert database date values or ISO date strings into date objects."""

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if not isinstance(value, str):
        return None

    value = value.strip()

    if not value:
        return None

    try:
        # Supports ISO dates and timestamps, including timezone suffixes.
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
        return parsed.date()
    except ValueError:
        pass

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def quote_identifier(identifier: str) -> str:
    """Safely quote a PostgreSQL table or column identifier."""
    return '"' + identifier.replace('"', '""') + '"'


async def get_date_column_profile(
    db: AsyncSession,
    dataset_id: int,
    date_column: str,
):
    dataset_result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = dataset_result.scalar_one_or_none()

    if dataset is None:
        return None

    table_name = quote_identifier(dataset.table_name)
    column_name = quote_identifier(date_column)

    query = text(
        f"""
        SELECT {column_name}
        FROM {table_name}
        WHERE {column_name} IS NOT NULL
          AND BTRIM(CAST({column_name} AS TEXT)) <> ''
        """
    )

    result = await db.execute(query)
    rows = result.fetchall()

    parsed_dates = [
        parsed
        for row in rows
        if (parsed := parse_date(row[0])) is not None
    ]

    if not parsed_dates:
        return {
            "column": date_column,
            "min_date": None,
            "max_date": None,
            "non_null_count": len(rows),
            "unique_dates": 0,
            "date_range_days": None,
        }

    min_date = min(parsed_dates)
    max_date = max(parsed_dates)

    return {
        "column": date_column,
        "min_date": min_date.isoformat(),
        "max_date": max_date.isoformat(),
        "non_null_count": len(rows),
        "unique_dates": len(set(parsed_dates)),
        "date_range_days": (max_date - min_date).days,
    }


def determine_date_granularity(date_profile: dict):
    date_range_days = date_profile.get("date_range_days")
    unique_dates = date_profile.get("unique_dates", 0)

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
    date_columns: list[str],
):
    date_profiles = []

    for date_column in date_columns:
        profile = await get_date_column_profile(
            db,
            dataset_id,
            date_column,
        )

        if profile is None:
            continue

        profile["granularity"] = determine_date_granularity(
            profile
        )
        date_profiles.append(profile)

    return date_profiles