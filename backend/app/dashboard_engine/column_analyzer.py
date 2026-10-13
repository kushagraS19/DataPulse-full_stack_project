
from typing import Any
from datetime import date, datetime

NUMERIC_TYPES = {
    "bigint",
    "integer",
    "smallint",
    "numeric",
    "double precision",
    "real",
}

CATEGORICAL_TYPES = {
    "text",
    "character varying",
    "character",
    "varchar",
    "boolean",
}

DATE_TYPES = {
    "date",
    "timestamp",
    "timestamp without time zone",
    "timestamp with time zone",
}


def _is_date_value(value: Any) -> bool:
    """Return True when a value can be parsed as a date."""
    if isinstance(value, (date, datetime)):
        return True

    if not isinstance(value, str):
        return False

    value = value.strip()

    if not value:
        return False

    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        pass

    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def classify_columns(
    columns: list[dict[str, Any]],
    statistics: list[dict[str, Any]],
):
    numeric_columns = []
    categorical_columns = []
    date_columns = []
    identifier_columns = []

    for column in columns:
        column_name = column["name"]
        data_type = column["data_type"].lower()

        column_stats = next(
            (
                stat
                for stat in statistics
                if stat["name"] == column_name
            ),
            None,
        )

        if column_stats is None:
            continue

        total_count = column_stats["total_count"]
        unique_count = column_stats["unique_count"]

        if data_type in NUMERIC_TYPES:
            name_lower = column_name.lower()

            is_id_name = (
                name_lower == "id"
                or name_lower.endswith("_id")
                or name_lower.endswith("id")
            )

            # High cardinality alone does not make a numeric field an ID:
            # sales, salary, prices, ratings, and measurements can all be unique.
            # Treat a numeric field as an identifier only when its name indicates one.
            if is_id_name:
                identifier_columns.append(column_name)
            else:
                numeric_columns.append(column_name)

        elif data_type in DATE_TYPES:
            date_columns.append(column_name)

        elif data_type in CATEGORICAL_TYPES:
            if total_count == 0:
                continue

            # Only inspect text columns with a date-like name.
            # This avoids scanning every text column unnecessarily.
            name_lower = column_name.lower()
            looks_like_date = any(
                keyword in name_lower
                for keyword in (
                    "date",
                    "time",
                    "timestamp",
                    "created_at",
                    "updated_at",
                )
            )

            if looks_like_date:
                # Classification based on the column's actual values
                # must be performed by the caller, which has access
                # to the dataset rows.
                continue

            cardinality_ratio = unique_count / total_count

            # Booleans are categorical regardless of their 2/total cardinality ratio.
            if data_type == "boolean":
                categorical_columns.append(column_name)
            elif cardinality_ratio >= 0.95:
                # High-cardinality text fields such as customer names are identifiers,
                # not useful categories for grouping every chart.
                identifier_columns.append(column_name)
            elif unique_count <= 50 and cardinality_ratio <= 0.5:
                categorical_columns.append(column_name)

    return {
        "numeric": numeric_columns,
        "categorical": categorical_columns,
        "date": date_columns,
        "identifier": identifier_columns,
    }
