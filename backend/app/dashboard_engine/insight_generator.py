def generate_insights(
    statistics: list[dict],
    identifier_columns: list[str],
    correlations: list[dict]
):
    insights = []

    for stat in statistics:

        if stat["missing_percentage"] > 0:

            insights.append({
                "type": "data_quality",
                "column": stat["name"],
                "message": (
                    f"{stat['name']} contains "
                    f"{stat['missing_percentage']}% "
                    f"missing values."
                ),
                "severity": (
                    "high"
                    if stat["missing_percentage"] > 30
                    else "medium"
                )
            })

    for column in identifier_columns:

        insights.append({
            "type": "column_detection",
            "column": column,
            "message": (
                f"{column} appears to be an "
                f"identifier column and was "
                f"excluded from analytics."
            ),
            "severity": "info"
        })

    for correlation in correlations:

        correlation_value = (
            correlation["correlation"]
        )

        if abs(correlation_value) < 0.7:
            continue

        if correlation_value > 0:
            relationship = "strong positive"
        else:
            relationship = "strong negative"

        insights.append({
            "type": "relationship",
            "column": (
                f"{correlation['x']} "
                f"and "
                f"{correlation['y']}"
            ),
            "message": (
                f"{correlation['x']} and "
                f"{correlation['y']} show a "
                f"{relationship} correlation "
                f"of {correlation_value}."
            ),
            "severity": "info"
        })

    return insights