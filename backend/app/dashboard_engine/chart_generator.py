def generate_charts(
    primary_numeric_column: str | None,
    primary_categorical_column: str | None,
    categorical_cardinality: int,
    date_profiles: list[dict],
    correlations: list[dict]
):
    charts = []

    if (
        primary_numeric_column
        and primary_categorical_column
    ):

        charts.append({
            "name": (
                f"{primary_numeric_column} "
                f"by "
                f"{primary_categorical_column}"
            ),
            "chart_type": "bar",
            "group_by": primary_categorical_column,
            "operation": "average",
            "column": primary_numeric_column
        })

    if (
        primary_categorical_column
        and categorical_cardinality <= 6
    ):

        charts.append({
            "name": (
                f"{primary_categorical_column} "
                f"Distribution"
            ),
            "chart_type": "pie",
            "group_by": primary_categorical_column,
            "operation": "count",
            "column": None
        })

    if (
        date_profiles
        and primary_numeric_column
    ):

        date_profile = date_profiles[0]

        date_column = date_profile["column"]

        charts.append({
            "name": (
                f"{primary_numeric_column} "
                f"over "
                f"{date_column}"
            ),
            "chart_type": "line",
            "group_by": date_column,
            "operation": "sum",
            "column": primary_numeric_column,
            "time_granularity": date_profile.get(
                "granularity"
            )
        })

    for correlation in correlations:

        correlation_value = (
            correlation["correlation"]
        )

        if abs(correlation_value) < 0.5:
            continue

        charts.append({
            "name": (
                f"{correlation['y']} "
                f"vs "
                f"{correlation['x']}"
            ),
            "chart_type": "scatter",
            "group_by": None,
            "operation": None,
            "column": None,
            "x_column": correlation["x"],
            "y_column": correlation["y"],
            "correlation": correlation_value
        })

    return charts