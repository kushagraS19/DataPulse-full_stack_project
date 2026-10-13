from __future__ import annotations

from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_model import Dataset


NUMERIC_SQL_TYPES = {
    "bigint", "integer", "smallint", "numeric",
    "double precision", "real", "decimal", "money",
}


def _quote_identifier(identifier: str) -> str:
    """Quote a PostgreSQL identifier safely."""
    return '"' + identifier.replace('"', '""') + '"'


def _number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if result == result and abs(result) != float("inf") else None


def _format_number(value: Any) -> str:
    number = _number(value)
    if number is None:
        return "not available"
    if abs(number) >= 1_000_000:
        return f"{number:,.0f}"
    if abs(number) >= 100:
        return f"{number:,.1f}".rstrip("0").rstrip(".")
    return f"{number:,.2f}".rstrip("0").rstrip(".")


def _insight(
    insight_type: str,
    column: str,
    message: str,
    severity: str = "info",
    **extra: Any,
) -> dict[str, Any]:
    return {
        "type": insight_type,
        "column": column,
        "message": message,
        "severity": severity,
        **extra,
    }


async def generate_insights(
    statistics: list[dict],
    identifier_columns: list[str],
    correlations: list[dict],
    *,
    db: AsyncSession | None = None,
    dataset_id: int | None = None,
    numeric_columns: list[str] | None = None,
    categorical_columns: list[str] | None = None,
    max_insights: int = 10,
) -> list[dict[str, Any]]:
    """Generate data-specific findings instead of repeating column-detection notes.

    Numeric summaries and category comparisons are computed in PostgreSQL. Identifier
    columns are deliberately omitted from the insight cards: they are implementation
    metadata, not business findings.
    """
    insights: list[dict[str, Any]] = []
    numeric_columns = list(dict.fromkeys(numeric_columns or []))
    categorical_columns = list(dict.fromkeys(categorical_columns or []))
    stats_by_name = {item.get("name"): item for item in statistics}

    # Data-quality findings are useful even when deeper profiling is unavailable.
    for stat in statistics:
        missing = _number(stat.get("missing_percentage")) or 0
        if missing > 0:
            severity = "high" if missing >= 20 else "medium" if missing >= 5 else "low"
            insights.append(_insight(
                "data_quality",
                stat.get("name", "dataset"),
                f"{stat.get('name')} has {missing:g}% missing values, which may affect comparisons using this field.",
                severity,
            ))

    # Keep actual relationships, but make the wording and strength explicit.
    for correlation in correlations:
        coefficient = _number(correlation.get("correlation"))
        x_column = correlation.get("x")
        y_column = correlation.get("y")
        if coefficient is None or not x_column or not y_column or abs(coefficient) < 0.5:
            continue
        strength = "strong" if abs(coefficient) >= 0.7 else "moderate"
        direction = "move together" if coefficient > 0 else "move in opposite directions"
        insights.append(_insight(
            "relationship",
            f"{x_column} and {y_column}",
            f"{x_column} and {y_column} have a {strength} {'positive' if coefficient > 0 else 'negative'} relationship (correlation {coefficient:.2f}); the values tend to {direction}. This is an association, not proof that one causes the other.",
            "info",
            correlation=round(coefficient, 3),
        ))

    # Profile real values only when the caller provides database context.
    if db is not None and dataset_id is not None:
        dataset_result = await db.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        dataset = dataset_result.scalar_one_or_none()

        if dataset is not None:
            table = _quote_identifier(dataset.table_name)

            # Numeric distributions: spread and potential extreme values.
            for column in numeric_columns:
                if len(insights) >= max_insights * 2:
                    break
                stat = stats_by_name.get(column, {})
                data_type = str(stat.get("data_type", "")).lower()
                if data_type and data_type not in NUMERIC_SQL_TYPES:
                    continue

                quoted = _quote_identifier(column)
                query = text(f"""
                    SELECT
                        COUNT({quoted}) AS non_null_count,
                        AVG({quoted}::double precision) AS mean_value,
                        MIN({quoted}) AS min_value,
                        MAX({quoted}) AS max_value,
                        percentile_cont(0.25) WITHIN GROUP (ORDER BY {quoted}::double precision) AS q1,
                        percentile_cont(0.75) WITHIN GROUP (ORDER BY {quoted}::double precision) AS q3
                    FROM {table}
                    WHERE {quoted} IS NOT NULL
                """)
                result = await db.execute(query)
                row = result.mappings().first()
                if not row or not row.get("non_null_count"):
                    continue

                minimum = _number(row.get("min_value"))
                maximum = _number(row.get("max_value"))
                mean = _number(row.get("mean_value"))
                q1 = _number(row.get("q1"))
                q3 = _number(row.get("q3"))

                # Only mention useful range information, not every column's basic stats.
                if minimum is not None and maximum is not None and q1 is not None and q3 is not None:
                    iqr = q3 - q1
                    if iqr > 0:
                        lower_fence = q1 - 1.5 * iqr
                        upper_fence = q3 + 1.5 * iqr
                        outlier_query = text(f"""
                            SELECT COUNT(*) AS outlier_count
                            FROM {table}
                            WHERE {quoted} IS NOT NULL
                              AND ({quoted}::double precision < :lower_fence
                                   OR {quoted}::double precision > :upper_fence)
                        """)
                        outlier_result = await db.execute(
                            outlier_query,
                            {"lower_fence": lower_fence, "upper_fence": upper_fence},
                        )
                        outlier_count = int(outlier_result.scalar() or 0)
                        total = int(row["non_null_count"])
                        outlier_pct = outlier_count / total * 100 if total else 0
                        if outlier_pct >= 1:
                            insights.append(_insight(
                                "distribution",
                                column,
                                f"{column} has {outlier_count:,} unusually low or high values ({outlier_pct:.1f}% of non-missing records) using the 1.5×IQR rule. Check these records before relying on averages.",
                                "medium" if outlier_pct >= 5 else "info",
                                outlier_count=outlier_count,
                                outlier_percentage=round(outlier_pct, 2),
                            ))

            # Compare real category averages for business metrics.
            metric_priority = ("sales", "revenue", "orders", "quantity", "amount", "salary", "rating", "age")
            ordered_metrics = [c for c in metric_priority if c in numeric_columns]
            ordered_metrics.extend(c for c in numeric_columns if c not in ordered_metrics)

            seen_segment_categories: set[str] = set()
            for category in categorical_columns:
                if len(insights) >= max_insights * 2:
                    break
                if category in seen_segment_categories:
                    continue
                cat_stat = stats_by_name.get(category, {})
                cardinality = cat_stat.get("unique_count")
                if cardinality is not None and not (2 <= int(cardinality) <= 20):
                    continue

                q_category = _quote_identifier(category)
                for metric in ordered_metrics[:4]:
                    q_metric = _quote_identifier(metric)
                    is_additive_metric = any(
                        token in metric.lower()
                        for token in ("sales", "revenue", "amount", "orders", "quantity")
                    )
                    query = text(f"""
                        SELECT
                            CAST({q_category} AS TEXT) AS category_value,
                            COUNT(*) AS record_count,
                            SUM({q_metric}::double precision) AS total_value,
                            AVG({q_metric}::double precision) AS average_value
                        FROM {table}
                        WHERE {q_category} IS NOT NULL
                          AND {q_metric} IS NOT NULL
                        GROUP BY {q_category}
                        HAVING COUNT(*) >= 3
                        LIMIT 20
                    """)
                    result = await db.execute(query)
                    groups = [dict(row) for row in result.mappings().all()]
                    if len(groups) < 2:
                        continue

                    # Use totals only when category sizes are reasonably comparable.
                    # Otherwise compare averages to avoid mistaking a larger group for better performance.
                    counts = [int(group.get("record_count") or 0) for group in groups]
                    group_size_ratio = max(counts) / max(min(counts), 1)
                    use_total = is_additive_metric and group_size_ratio <= 1.5
                    value_key = "total_value" if use_total else "average_value"
                    groups.sort(
                        key=lambda group: _number(group.get(value_key))
                        if _number(group.get(value_key)) is not None else float("-inf"),
                        reverse=True,
                    )
                    best = groups[0]
                    worst = groups[-1]
                    best_value = _number(best.get(value_key))
                    worst_value = _number(worst.get(value_key))
                    if best_value is None or worst_value is None:
                        continue

                    difference = best_value - worst_value
                    scale = max(abs(best_value), abs(worst_value), 1e-9)
                    relative_gap = abs(difference) / scale * 100
                    if relative_gap < 10:
                        continue

                    metric_label = "total" if use_total else "average"
                    message = (
                        f"{best['category_value']} has the highest {metric_label} {metric} by {category} "
                        f"({_format_number(best_value)}), while {worst['category_value']} is lowest "
                        f"({_format_number(worst_value)}). The gap is {_format_number(abs(difference))} "
                        f"({relative_gap:.1f}% relative to the larger value)."
                    )
                    insights.append(_insight(
                        "segment_comparison",
                        f"{metric} by {category}",
                        message,
                        "info",
                        dimension=category,
                        metric=metric,
                        highest_category=str(best["category_value"]),
                        lowest_category=str(worst["category_value"]),
                        difference=round(difference, 3),
                        relative_gap_percentage=round(relative_gap, 2),
                    ))
                    seen_segment_categories.add(category)
                    break

                if len(insights) >= max_insights * 2:
                    break

            # Surface skewed category distributions, e.g. a city or department dominates.
            for category in categorical_columns:
                if len(insights) >= max_insights * 2:
                    break
                cat_stat = stats_by_name.get(category, {})
                cardinality = cat_stat.get("unique_count")
                total_count = _number(cat_stat.get("total_count")) or 0
                if cardinality is not None and not (2 <= int(cardinality) <= 20):
                    continue
                if total_count <= 0:
                    continue

                q_category = _quote_identifier(category)
                query = text(f"""
                    SELECT CAST({q_category} AS TEXT) AS category_value, COUNT(*) AS record_count
                    FROM {table}
                    WHERE {q_category} IS NOT NULL
                    GROUP BY {q_category}
                    ORDER BY record_count DESC
                    LIMIT 2
                """)
                result = await db.execute(query)
                groups = [dict(row) for row in result.mappings().all()]
                if not groups:
                    continue
                top = groups[0]
                share = int(top["record_count"]) / total_count * 100
                expected_share = 100 / max(int(cardinality or 1), 1)
                if share >= expected_share * 1.5:
                    insights.append(_insight(
                        "category_distribution",
                        category,
                        f"{top['category_value']} is the most common {category} group, representing {share:.1f}% of all records. The dataset is not evenly distributed across {category} values.",
                        "info",
                        dominant_category=str(top["category_value"]),
                        share_percentage=round(share, 2),
                    ))

    # Do not emit identifier-detection messages as user-facing insights. They are
    # already available in detected_columns and are not meaningful findings.
    # De-duplicate messages and cap the response to a compact set of useful cards.
    deduplicated: list[dict[str, Any]] = []
    seen_messages: set[str] = set()
    for item in insights:
        message = item.get("message", "")
        if message and message not in seen_messages:
            deduplicated.append(item)
            seen_messages.add(message)

    # Prioritize segment comparisons and relationships over generic data-quality notes.
    priority = {
        "segment_comparison": 0,
        "relationship": 1,
        "distribution": 2,
        "category_distribution": 3,
        "data_quality": 4,
    }
    deduplicated.sort(key=lambda item: priority.get(item.get("type"), 5))
    return deduplicated[:max_insights]
