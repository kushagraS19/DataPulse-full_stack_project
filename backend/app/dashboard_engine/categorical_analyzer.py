CATEGORICAL_KEYWORDS = [
    "category",
    "department",
    "dept",
    "type",
    "status",
    "region",
    "country",
    "state",
    "city",
    "segment",
    "product",
    "brand",
    "gender"
]


def get_primary_categorical_column(
    categorical_columns: list[str],
    statistics: list[dict]
):
    primary_categorical_column = None
    best_score = -1
    best_cardinality = 0

    for column in categorical_columns:

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

        unique_count = column_stats["unique_count"]

        column_lower = column.lower()

        score = 0

        if any(
            keyword in column_lower
            for keyword in CATEGORICAL_KEYWORDS
        ):
            score += 10

        if unique_count <= 6:
            score += 5

        if unique_count <= 20:
            score += 2

        if score > best_score:

            best_score = score
            best_cardinality = unique_count
            primary_categorical_column = column

    return {
        "column": primary_categorical_column,
        "cardinality": best_cardinality,
        "score": best_score
    }