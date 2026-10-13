from __future__ import annotations

from typing import Any


def _chart(
    name: str,
    chart_type: str,
    group_by: str | None = None,
    operation: str | None = None,
    column: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "name": name,
        "chart_type": chart_type,
        "group_by": group_by,
        "operation": operation,
        "column": column,
        **extra,
    }


def generate_charts(
    primary_numeric_column: str | None = None,
    primary_categorical_column: str | None = None,
    categorical_cardinality: int = 0,
    date_profiles: list[dict] | None = None,
    correlations: list[dict] | None = None,
    numeric_columns: list[str] | None = None,
    categorical_columns: list[str] | None = None,
    statistics: list[dict] | None = None,
    max_charts: int = 12,
) -> list[dict[str, Any]]:
    """Generate a balanced dashboard using supported ECharts chart types.

    Data requirements:
    - Aggregated charts use group_by + operation + column.
    - histogram/boxplot return raw values for column.
    - heatmap returns raw numeric x/y pairs for binning in the frontend.
    """
    date_profiles = date_profiles or []
    correlations = correlations or []
    numeric_columns = list(dict.fromkeys(numeric_columns or []))
    categorical_columns = list(dict.fromkeys(categorical_columns or []))
    statistics = statistics or []

    if not numeric_columns and primary_numeric_column:
        numeric_columns = [primary_numeric_column]
    if not categorical_columns and primary_categorical_column:
        categorical_columns = [primary_categorical_column]

    stats_by_name = {
        stat.get("name"): stat
        for stat in statistics
        if stat.get("name") is not None
    }

    pools: dict[str, list[dict[str, Any]]] = {
        "bar": [],
        "horizontal_bar": [],
        "pie": [],
        "donut": [],
        "line": [],
        "area": [],
        "scatter": [],
        "radar": [],
        "histogram": [],
        "boxplot": [],
        "heatmap": [],
    }

    # Bar charts: averages by categorical dimension.
    for category in categorical_columns:
        for numeric in numeric_columns:
            pools["bar"].append(_chart(
                name=f"Average {numeric} by {category}",
                chart_type="bar",
                group_by=category,
                operation="average",
                column=numeric,
            ))
            pools["horizontal_bar"].append(_chart(
                name=f"{numeric} by {category} (horizontal)",
                chart_type="horizontal_bar",
                group_by=category,
                operation="average",
                column=numeric,
                orientation="horizontal",
            ))

    # Composition charts are appropriate only for low-cardinality fields.
    for category in categorical_columns:
        cardinality = stats_by_name.get(category, {}).get("unique_count")
        if cardinality is None and category == primary_categorical_column:
            cardinality = categorical_cardinality
        if cardinality is not None and 2 <= cardinality <= 6:
            pools["pie"].append(_chart(
                name=f"{category} distribution",
                chart_type="pie",
                group_by=category,
                operation="count",
                column=None,
            ))
            pools["donut"].append(_chart(
                name=f"{category} share",
                chart_type="donut",
                group_by=category,
                operation="count",
                column=None,
            ))

    # Date charts use different measures to avoid duplicate visualizations.
    preferred_measures = [
        c for c in ("sales", "revenue", "amount", "orders", "quantity")
        if c in numeric_columns
    ]
    preferred_measures.extend(c for c in numeric_columns if c not in preferred_measures)

    for profile in date_profiles:
        date_column = profile.get("column")
        if not date_column:
            continue
        for index, numeric in enumerate(preferred_measures[:4]):
            lower_name = numeric.lower()
            operation = "sum" if any(
                token in lower_name
                for token in ("sales", "revenue", "amount", "orders", "quantity", "count")
            ) else "average"
            chart_type = "line" if index % 2 == 0 else "area"
            pools[chart_type].append(_chart(
                name=f"{numeric} over {date_column}",
                chart_type=chart_type,
                group_by=date_column,
                operation=operation,
                column=numeric,
                time_granularity=profile.get("granularity"),
            ))

    # Scatter plots for meaningful correlations.
    seen_pairs: set[tuple[str, str]] = set()
    for correlation in correlations:
        x_column = correlation.get("x")
        y_column = correlation.get("y")
        value = correlation.get("correlation")
        if not x_column or not y_column or value is None:
            continue
        try:
            coefficient = float(value)
        except (TypeError, ValueError):
            continue
        pair = tuple(sorted((x_column, y_column)))
        if abs(coefficient) < 0.3 or pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        pools["scatter"].append(_chart(
            name=f"{y_column} vs {x_column}",
            chart_type="scatter",
            x_column=x_column,
            y_column=y_column,
            correlation=round(coefficient, 3),
        ))

    # Radar charts compare one numeric measure across a modest number of categories.
    for category in categorical_columns:
        cardinality = stats_by_name.get(category, {}).get("unique_count", 0)
        if 3 <= cardinality <= 8:
            for numeric in numeric_columns[:2]:
                pools["radar"].append(_chart(
                    name=f"{numeric} profile by {category}",
                    chart_type="radar",
                    group_by=category,
                    operation="average",
                    column=numeric,
                ))

    # Raw numeric values feed histograms and box plots.
    for numeric in numeric_columns[:4]:
        pools["histogram"].append(_chart(
            name=f"{numeric} distribution (histogram)",
            chart_type="histogram",
            column=numeric,
        ))
        pools["boxplot"].append(_chart(
            name=f"{numeric} spread and outliers (box plot)",
            chart_type="boxplot",
            column=numeric,
        ))

    # Heatmap bins two numeric columns into a 2D density grid.
    if len(numeric_columns) >= 2:
        x_column, y_column = numeric_columns[:2]
        pools["heatmap"].append(_chart(
            name=f"{x_column} and {y_column} density (heatmap)",
            chart_type="heatmap",
            x_column=x_column,
            y_column=y_column,
        ))

    # Pick one from each available type first, then fill remaining slots round-robin.
    priority = [
        "line", "area", "bar", "horizontal_bar", "scatter", "histogram",
        "boxplot", "heatmap", "radar", "donut", "pie",
    ]
    selected: list[dict[str, Any]] = []
    used_signatures: set[tuple[Any, ...]] = set()

    def add_chart(chart: dict[str, Any]) -> None:
        signature = (
            chart.get("chart_type"), chart.get("group_by"), chart.get("operation"),
            chart.get("column"), chart.get("x_column"), chart.get("y_column"),
        )
        if signature not in used_signatures and len(selected) < max_charts:
            used_signatures.add(signature)
            selected.append(chart)

    for chart_type in priority:
        if pools[chart_type]:
            add_chart(pools[chart_type].pop(0))

    while len(selected) < max_charts and any(pools.values()):
        progressed = False
        for chart_type in priority:
            if pools[chart_type] and len(selected) < max_charts:
                add_chart(pools[chart_type].pop(0))
                progressed = True
        if not progressed:
            break

    return selected
