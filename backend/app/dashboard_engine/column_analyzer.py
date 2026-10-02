from typing import Any


NUMERIC_TYPES = {
    "bigint",
    "integer",
    "smallint",
    "numeric",
    "double precision",
    "real"
}


CATEGORICAL_TYPES = {
    "text",
    "character varying",
    "character",
    "varchar"
}


DATE_TYPES = {
    "date",
    "timestamp",
    "timestamp without time zone",
    "timestamp with time zone"
}


def classify_columns(
    columns: list[dict[str, Any]],
    statistics: list[dict[str, Any]]
):
    numeric_columns = []
    categorical_columns = []
    date_columns = []
    identifier_columns = []

    for column in columns:

        column_name = column["name"]
        data_type = column["data_type"]

        column_stats = next(
            (
                stat
                for stat in statistics
                if stat["name"] == column_name
            ),
            None
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

            is_high_cardinality = (
                total_count > 0
                and unique_count / total_count >= 0.95
            )

            if is_id_name or is_high_cardinality:

                identifier_columns.append(
                    column_name
                )

            else:

                numeric_columns.append(
                    column_name
                )

        elif data_type in CATEGORICAL_TYPES:

            if total_count == 0:
                continue

            cardinality_ratio = (
                unique_count / total_count
            )

            if (
                unique_count <= 20
                and cardinality_ratio <= 0.5
            ):

                categorical_columns.append(
                    column_name
                )

        elif data_type in DATE_TYPES:

            date_columns.append(
                column_name
            )

    return {
        "numeric": numeric_columns,
        "categorical": categorical_columns,
        "date": date_columns,
        "identifier": identifier_columns
    }