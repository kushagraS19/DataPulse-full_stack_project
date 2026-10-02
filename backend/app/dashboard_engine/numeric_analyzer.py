from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_model import Dataset


NUMERIC_KEYWORDS = {
    "revenue": 15,
    "sales": 15,
    "profit": 15,
    "income": 12,
    "salary": 12,
    "amount": 10,
    "price": 10,
    "cost": 10,
    "total": 8,
    "value": 8,
    "quantity": 6,
    "count": 4,
    "units": 4
}


def calculate_numeric_scores(
    numeric_columns: list[str],
    statistics: list[dict]
):
    numeric_scores = {}

    for column in numeric_columns:

        column_stats = next(
            (
                stat
                for stat in statistics
                if stat["name"] == column
            ),
            None
        )

        if column_stats is None:
            continue

        score = 0

        column_lower = column.lower()

        for keyword, points in NUMERIC_KEYWORDS.items():

            if keyword in column_lower:
                score += points

        missing_percentage = (
            column_stats["missing_percentage"]
        )

        if missing_percentage == 0:

            score += 10

        elif missing_percentage <= 10:

            score += 7

        elif missing_percentage <= 20:

            score += 4

        elif missing_percentage <= 30:

            score += 1

        else:

            score -= 20

        total_count = column_stats["total_count"]
        unique_count = column_stats["unique_count"]

        if total_count > 0:

            cardinality_ratio = (
                unique_count / total_count
            )

            if cardinality_ratio >= 0.1:
                score += 3

            if cardinality_ratio >= 0.9:
                score -= 5

        numeric_scores[column] = score

    return numeric_scores


def get_reliable_numeric_columns(
    numeric_columns: list[str],
    statistics: list[dict]
):
    reliable_numeric_columns = []

    for column in numeric_columns:

        column_stats = next(
            (
                stat
                for stat in statistics
                if stat["name"] == column
            ),
            None
        )

        if column_stats is None:
            continue

        if column_stats.get(
            "missing_percentage",
            100
        ) <= 30:

            reliable_numeric_columns.append(
                column
            )

    return reliable_numeric_columns


def get_primary_numeric_column(
    reliable_numeric_columns: list[str],
    numeric_scores: dict
):
    if not reliable_numeric_columns:
        return None

    return max(
        reliable_numeric_columns,
        key=lambda column: numeric_scores.get(
            column,
            0
        )
    )


def rank_numeric_columns(
    reliable_numeric_columns: list[str],
    numeric_scores: dict
):
    return sorted(
        reliable_numeric_columns,
        key=lambda column: numeric_scores.get(
            column,
            0
        ),
        reverse=True
    )


def create_numeric_pairs(
    ranked_numeric_columns: list[str]
):
    numeric_pairs = []

    for index, first_column in enumerate(
        ranked_numeric_columns
    ):

        for second_column in ranked_numeric_columns[
            index + 1:
        ]:

            numeric_pairs.append({
                "x": first_column,
                "y": second_column
            })

            if len(numeric_pairs) >= 3:
                break

        if len(numeric_pairs) >= 3:
            break

    return numeric_pairs


async def calculate_numeric_correlations(
    db: AsyncSession,
    dataset_id: int,
    pairs: list[dict]
):
    dataset_result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = dataset_result.scalar_one_or_none()

    if dataset is None:
        return None

    correlations = []

    for pair in pairs:

        x_column = pair["x"]
        y_column = pair["y"]

        query = text(
            f'''
            SELECT
                CORR(
                    "{x_column}",
                    "{y_column}"
                ) AS correlation
            FROM "{dataset.table_name}"
            '''
        )

        result = await db.execute(query)

        row = result.fetchone()

        if row is None:
            continue

        correlation = row.correlation

        if correlation is None:
            continue

        correlations.append({
            "x": x_column,
            "y": y_column,
            "correlation": round(
                float(correlation),
                4
            )
        })

    return correlations