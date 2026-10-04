# ============================================================
# IMPORTS
# ============================================================

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.services.data_profiling_services import profile_dataset


# ============================================================
# CONSTANTS
# ============================================================

MAX_INSIGHTS = 20

SEVERITY_PRIORITY = {
    "critical": 4,
    "warning": 3,
    "info": 2,
    "success": 1,
}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def _safe_float(value: Any) -> float | None:
    """
    Convert a value to float safely.
    """

    if value is None:
        return None

    try:
        result = float(value)

        if not np.isfinite(result):
            return None

        return result

    except (TypeError, ValueError):
        return None


def _round_value(
    value: Any,
    digits: int = 2
) -> Any:
    """
    Safely round numeric values.
    """

    numeric_value = _safe_float(value)

    if numeric_value is None:
        return value

    return round(
        numeric_value,
        digits
    )


def _get_numeric_columns(
    df: pd.DataFrame
) -> list[str]:
    """
    Return numeric columns from a DataFrame.
    """

    return [
        str(column)
        for column in df.select_dtypes(
            include=np.number
        ).columns
    ]


def _get_datetime_columns(
    df: pd.DataFrame
) -> list[str]:
    """
    Detect datetime columns.
    """

    datetime_columns = []

    for column in df.columns:

        if pd.api.types.is_datetime64_any_dtype(
            df[column]
        ):
            datetime_columns.append(
                str(column)
            )
            continue

        converted = pd.to_datetime(
            df[column],
            errors="coerce"
        )

        if (
            df[column].notna().sum() > 0
            and converted.notna().sum()
            == df[column].notna().sum()
        ):
            datetime_columns.append(
                str(column)
            )

    return datetime_columns


# ============================================================
# 5.2 NUMERIC INSIGHTS
# ============================================================

def generate_numeric_insights(
    column_profile: dict
) -> list[dict]:
    """
    Generate insights for a numeric column.
    """

    insights = []

    column = column_profile.get(
        "column"
    )

    statistics = column_profile.get(
        "statistics"
    )

    if not statistics:
        return insights

    minimum = statistics.get("min")
    maximum = statistics.get("max")
    mean = statistics.get("mean")
    median = statistics.get("median")
    std = statistics.get("std")

    outliers = statistics.get(
        "outliers",
        {}
    )

    if mean is None or median is None:
        return insights

    mean_value = _safe_float(mean)
    median_value = _safe_float(median)

    if (
        mean_value is not None
        and median_value is not None
        and mean_value != 0
    ):
        difference_percentage = (
            abs(mean_value - median_value)
            / abs(mean_value)
        ) * 100

        if difference_percentage >= 20:

            direction = (
                "higher"
                if mean_value > median_value
                else "lower"
            )

            insights.append({
                "type": "distribution",
                "severity": "info",
                "title": (
                    f"{column} may have an uneven distribution"
                ),
                "description": (
                    f"The mean is "
                    f"{difference_percentage:.1f}% "
                    f"{direction} than the median."
                ),
                "column": column,
                "value": round(
                    difference_percentage,
                    2
                ),
            })

    std_value = _safe_float(std)

    if (
        std_value is not None
        and mean_value is not None
        and mean_value != 0
    ):
        coefficient_of_variation = (
            abs(std_value / mean_value)
        ) * 100

        if coefficient_of_variation >= 50:

            insights.append({
                "type": "variation",
                "severity": "info",
                "title": (
                    f"{column} has high variation"
                ),
                "description": (
                    f"The standard deviation is "
                    f"{coefficient_of_variation:.1f}% "
                    f"of the mean."
                ),
                "column": column,
                "value": round(
                    coefficient_of_variation,
                    2
                ),
            })

    outlier_count = int(
        outliers.get(
            "count",
            0
        )
    )

    outlier_percentage = _safe_float(
        outliers.get(
            "percentage",
            0
        )
    ) or 0.0

    if outlier_count > 0:

        severity = (
            "warning"
            if outlier_percentage >= 5
            else "info"
        )

        insights.append({
            "type": "outlier",
            "severity": severity,
            "title": (
                f"{column} contains outliers"
            ),
            "description": (
                f"{outlier_count} values "
                f"({outlier_percentage:.2f}%) "
                f"were identified as potential outliers."
            ),
            "column": column,
            "value": outlier_count,
            "percentage": round(
                outlier_percentage,
                2
            ),
        })

    minimum_value = _safe_float(
        minimum
    )

    maximum_value = _safe_float(
        maximum
    )

    if (
        minimum_value is not None
        and maximum_value is not None
    ):
        value_range = (
            maximum_value - minimum_value
        )

        if value_range > 0:

            insights.append({
                "type": "range",
                "severity": "info",
                "title": (
                    f"{column} has a wide value range"
                ),
                "description": (
                    f"Values range from "
                    f"{minimum} to {maximum}."
                ),
                "column": column,
                "value": _round_value(
                    value_range
                ),
            })

    return insights


# ============================================================
# 5.3 CATEGORICAL INSIGHTS
# ============================================================

def generate_categorical_insights(
    column_profile: dict,
    value_counts: dict | None = None
) -> list[dict]:

    insights = []

    column = column_profile.get(
        "column"
    )

    unique_count = column_profile.get(
        "unique_count",
        0
    )

    non_null_count = column_profile.get(
        "non_null_count",
        0
    )

    is_high_cardinality = column_profile.get(
        "is_high_cardinality",
        False
    )

    if (
        not column
        or non_null_count == 0
        or not value_counts
    ):
        return insights

    sorted_categories = sorted(
        value_counts.items(),
        key=lambda item: item[1],
        reverse=True
    )

    top_category, top_count = (
        sorted_categories[0]
    )

    top_percentage = (
        top_count / non_null_count
    ) * 100

    if top_percentage >= 50:

        insights.append({
            "type": "dominant_category",
            "severity": "info",
            "title": (
                f"{top_category} dominates {column}"
            ),
            "description": (
                f"{top_category} represents "
                f"{top_percentage:.1f}% of "
                f"non-null values."
            ),
            "column": column,
            "category": str(
                top_category
            ),
            "value": int(
                top_count
            ),
            "percentage": round(
                top_percentage,
                2
            ),
        })

    if len(sorted_categories) >= 2:

        second_category, second_count = (
            sorted_categories[1]
        )

        second_percentage = (
            second_count / non_null_count
        ) * 100

        if top_percentage >= 30:

            insights.append({
                "type": "category_distribution",
                "severity": "info",
                "title": (
                    f"{column} has a leading category"
                ),
                "description": (
                    f"{top_category} is the most common "
                    f"value at {top_percentage:.1f}%, "
                    f"followed by {second_category} "
                    f"at {second_percentage:.1f}%."
                ),
                "column": column,
                "top_category": str(
                    top_category
                ),
                "top_percentage": round(
                    top_percentage,
                    2
                ),
                "second_category": str(
                    second_category
                ),
                "second_percentage": round(
                    second_percentage,
                    2
                ),
            })

    rare_categories = []

    for category, count in sorted_categories:

        percentage = (
            count / non_null_count
        ) * 100

        if percentage < 1:

            rare_categories.append({
                "category": str(
                    category
                ),
                "count": int(
                    count
                ),
                "percentage": round(
                    percentage,
                    2
                ),
            })

    if rare_categories:

        insights.append({
            "type": "rare_categories",
            "severity": "info",
            "title": (
                f"{column} contains rare categories"
            ),
            "description": (
                f"{len(rare_categories)} categories "
                f"represent less than 1% each."
            ),
            "column": column,
            "category_count": len(
                rare_categories
            ),
            "categories": rare_categories[:10],
        })

    if is_high_cardinality:

        insights.append({
            "type": "high_cardinality",
            "severity": "warning",
            "title": (
                f"{column} has high cardinality"
            ),
            "description": (
                f"{unique_count} unique values were "
                f"found across {non_null_count} "
                f"non-null records."
            ),
            "column": column,
            "unique_count": unique_count,
            "non_null_count": non_null_count,
        })

    return insights


# ============================================================
# 5.4 DATETIME INSIGHTS
# ============================================================

def generate_datetime_insights(
    column_profile: dict
) -> list[dict]:

    insights = []

    column = column_profile.get(
        "column"
    )

    date_profile = column_profile.get(
        "date_profile"
    )

    if not column or not date_profile:
        return insights

    minimum = date_profile.get(
        "min"
    )

    maximum = date_profile.get(
        "max"
    )

    range_days = date_profile.get(
        "range_days"
    )

    frequency = date_profile.get(
        "frequency"
    )

    if minimum is None or maximum is None:
        return insights

    if range_days is not None:

        if range_days == 0:

            description = (
                f"All records in {column} "
                f"occur on the same date."
            )

        else:

            description = (
                f"The {column} column spans "
                f"{range_days:,} days, from "
                f"{minimum} to {maximum}."
            )

        insights.append({
            "type": "date_range",
            "severity": "info",
            "title": (
                f"{column} spans a date range"
            ),
            "description": description,
            "column": column,
            "min_date": minimum,
            "max_date": maximum,
            "range_days": range_days,
        })

    if frequency:

        insights.append({
            "type": "date_frequency",
            "severity": "info",
            "title": (
                f"{column} has {frequency} frequency"
            ),
            "description": (
                f"The values in {column} appear "
                f"to follow a {frequency} pattern."
            ),
            "column": column,
            "frequency": frequency,
        })

    if (
        range_days is not None
        and range_days <= 31
    ):

        insights.append({
            "type": "short_date_range",
            "severity": "info",
            "title": (
                f"{column} covers a short time period"
            ),
            "description": (
                f"The dataset covers only "
                f"{range_days} days."
            ),
            "column": column,
            "range_days": range_days,
        })

    if (
        range_days is not None
        and range_days >= 365
    ):

        years = round(
            range_days / 365,
            1
        )

        insights.append({
            "type": "long_date_range",
            "severity": "info",
            "title": (
                f"{column} covers a long time period"
            ),
            "description": (
                f"The dataset spans approximately "
                f"{years} years."
            ),
            "column": column,
            "range_days": range_days,
            "years": years,
        })

    return insights


# ============================================================
# 5.5 CORRELATION INSIGHTS
# ============================================================

def generate_correlation_insights(
    correlations: list[dict]
) -> list[dict]:

    insights = []

    for correlation_data in correlations:

        x_column = correlation_data.get(
            "x"
        )

        y_column = correlation_data.get(
            "y"
        )

        correlation = _safe_float(
            correlation_data.get(
                "correlation"
            )
        )

        if (
            x_column is None
            or y_column is None
            or correlation is None
        ):
            continue

        absolute_correlation = abs(
            correlation
        )

        if absolute_correlation >= 0.70:
            strength = "strong"

        elif absolute_correlation >= 0.30:
            strength = "moderate"

        else:
            continue

        if correlation >= 0.30:
            direction = "positive"

        else:
            direction = "negative"

        if direction == "positive":

            description = (
                f"{x_column} and {y_column} have "
                f"a {strength} positive correlation "
                f"of {correlation:.2f}."
            )

        else:

            description = (
                f"{x_column} and {y_column} have "
                f"a {strength} negative correlation "
                f"of {correlation:.2f}."
            )

        insights.append({
            "type": "correlation",
            "severity": (
                "warning"
                if absolute_correlation >= 0.70
                else "info"
            ),
            "title": (
                f"{strength.capitalize()} "
                f"{direction} relationship between "
                f"{x_column} and {y_column}"
            ),
            "description": description,
            "columns": [
                x_column,
                y_column,
            ],
            "correlation": round(
                correlation,
                4
            ),
            "strength": strength,
            "direction": direction,
        })

    return insights


# ============================================================
# 5.6 OUTLIER INSIGHTS
# ============================================================

def generate_outlier_insights(
    column_profiles: list[dict]
) -> list[dict]:

    insights = []

    for column_profile in column_profiles:

        statistics = column_profile.get(
            "statistics"
        )

        if not statistics:
            continue

        column = column_profile.get(
            "column"
        )

        outliers = statistics.get(
            "outliers",
            {}
        )

        count = int(
            outliers.get(
                "count",
                0
            )
        )

        percentage = _safe_float(
            outliers.get(
                "percentage",
                0
            )
        ) or 0.0

        if count == 0:
            continue

        if percentage >= 10:
            severity = "critical"

        elif percentage >= 5:
            severity = "warning"

        else:
            severity = "info"

        insights.append({
            "type": "outlier",
            "severity": severity,
            "title": (
                f"{column} contains "
                f"{count} potential outliers"
            ),
            "description": (
                f"{percentage:.2f}% of values in "
                f"{column} were identified as "
                f"potential outliers using the "
                f"IQR method."
            ),
            "column": column,
            "count": count,
            "percentage": round(
                percentage,
                2
            ),
            "lower_bound": outliers.get(
                "lower_bound"
            ),
            "upper_bound": outliers.get(
                "upper_bound"
            ),
        })

    return insights


# ============================================================
# 5.7 DATA QUALITY INSIGHTS
# ============================================================

def generate_quality_insights(
    profile: dict
) -> list[dict]:

    insights = []

    summary = profile.get(
        "summary",
        {}
    )

    columns = profile.get(
        "columns",
        []
    )

    row_count = summary.get(
        "row_count",
        0
    )

    duplicate_rows = summary.get(
        "duplicate_rows",
        {}
    )

    duplicate_count = int(
        duplicate_rows.get(
            "count",
            0
        )
    )

    duplicate_percentage = _safe_float(
        duplicate_rows.get(
            "percentage",
            0
        )
    ) or 0.0

    # --------------------------------------------------------
    # Duplicate rows
    # --------------------------------------------------------

    if duplicate_count > 0:

        severity = (
            "warning"
            if duplicate_percentage >= 5
            else "info"
        )

        insights.append({
            "type": "duplicate_rows",
            "severity": severity,
            "title": (
                f"{duplicate_count} duplicate rows detected"
            ),
            "description": (
                f"{duplicate_percentage:.2f}% of dataset "
                f"rows are duplicates."
            ),
            "value": duplicate_count,
            "percentage": round(
                duplicate_percentage,
                2
            ),
        })

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    for column in columns:

        column_name = column.get(
            "column"
        )

        missing_count = int(
            column.get(
                "missing_count",
                0
            )
        )

        missing_percentage = _safe_float(
            column.get(
                "missing_percentage",
                0
            )
        ) or 0.0

        if missing_count == 0:
            continue

        if missing_percentage >= 30:
            severity = "critical"

        elif missing_percentage >= 10:
            severity = "warning"

        else:
            severity = "info"

        insights.append({
            "type": "missing_values",
            "severity": severity,
            "title": (
                f"{column_name} contains missing values"
            ),
            "description": (
                f"{missing_count} values are missing "
                f"from {column_name}, representing "
                f"{missing_percentage:.2f}% of the column."
            ),
            "column": column_name,
            "count": missing_count,
            "percentage": round(
                missing_percentage,
                2
            ),
        })

    # --------------------------------------------------------
    # Constant columns
    # --------------------------------------------------------

    for column in columns:

        if column.get(
            "is_constant",
            False
        ):

            column_name = column.get(
                "column"
            )

            insights.append({
                "type": "constant_column",
                "severity": "warning",
                "title": (
                    f"{column_name} contains "
                    f"only one unique value"
                ),
                "description": (
                    f"{column_name} is constant across "
                    f"all non-null records and may not "
                    f"provide useful analytical information."
                ),
                "column": column_name,
            })

    return insights


# ============================================================
# 5.8 INSIGHT PRIORITIZATION
# ============================================================

def prioritize_insights(
    insights: list[dict],
    limit: int = MAX_INSIGHTS
) -> list[dict]:
    """
    Sort insights by severity and remove duplicates.
    """

    unique_insights = []
    seen = set()

    for insight in insights:

        key = (
            insight.get("type"),
            insight.get("column"),
            tuple(
                insight.get(
                    "columns",
                    []
                )
            ),
            insight.get("title"),
        )

        if key in seen:
            continue

        seen.add(key)
        unique_insights.append(
            insight
        )

    unique_insights.sort(
        key=lambda insight: (
            SEVERITY_PRIORITY.get(
                insight.get(
                    "severity",
                    "info"
                ),
                0
            )
        ),
        reverse=True
    )

    return unique_insights[:limit]


# ============================================================
# 5.9 COMPLETE INSIGHT ENGINE
# ============================================================

def generate_dataset_insights(
    df: pd.DataFrame,
    correlation_threshold: float = 0.30,
    limit: int = MAX_INSIGHTS
) -> dict[str, Any]:
    """
    Run the complete automatic insight engine.

    The DataFrame is loaded once and all insight detectors
    operate on the same dataset.
    """

    if not isinstance(
        df,
        pd.DataFrame
    ):
        raise TypeError(
            "generate_dataset_insights expects "
            "a Pandas DataFrame"
        )

    if df.empty:
        raise ValueError(
            "Cannot generate insights "
            "for an empty dataset"
        )

    profile = profile_dataset(
        df
    )

    all_insights = []

    column_profiles = profile.get(
        "columns",
        []
    )

    # --------------------------------------------------------
    # Numeric + categorical + datetime insights
    # --------------------------------------------------------

    for column_profile in column_profiles:

        data_type = column_profile.get(
            "data_type"
        )

        column = column_profile.get(
            "column"
        )

        if not column:
            continue

        if data_type == "numeric":

            all_insights.extend(
                generate_numeric_insights(
                    column_profile
                )
            )

        elif data_type == "datetime":

            all_insights.extend(
                generate_datetime_insights(
                    column_profile
                )
            )

        elif data_type == "text":

            value_counts = (
                df[column]
                .value_counts(
                    dropna=False
                )
                .to_dict()
            )

            all_insights.extend(
                generate_categorical_insights(
                    column_profile,
                    value_counts
                )
            )

    # --------------------------------------------------------
    # Outlier insights
    # --------------------------------------------------------

    all_insights.extend(
        generate_outlier_insights(
            column_profiles
        )
    )

    # --------------------------------------------------------
    # Data quality insights
    # --------------------------------------------------------

    all_insights.extend(
        generate_quality_insights(
            profile
        )
    )

    # --------------------------------------------------------
    # Correlation insights
    # --------------------------------------------------------

    numeric_columns = (
        _get_numeric_columns(df)
    )

    if len(numeric_columns) >= 2:

        correlation_matrix = (
            df[numeric_columns]
            .corr()
        )

        correlations = []

        for index, x_column in enumerate(
            numeric_columns
        ):

            for y_column in numeric_columns[
                index + 1:
            ]:

                correlation = (
                    correlation_matrix.loc[
                        x_column,
                        y_column
                    ]
                )

                if pd.isna(
                    correlation
                ):
                    continue

                if abs(
                    correlation
                ) < correlation_threshold:
                    continue

                correlations.append({
                    "x": x_column,
                    "y": y_column,
                    "correlation": round(
                        float(correlation),
                        4
                    ),
                })

        all_insights.extend(
            generate_correlation_insights(
                correlations
            )
        )

    # --------------------------------------------------------
    # Prioritize
    # --------------------------------------------------------

    prioritized = prioritize_insights(
        all_insights,
        limit=limit
    )

    return {
        "dataset": {
            "row_count": len(df),
            "column_count": len(df.columns),
        },
        "insight_count": len(
            prioritized
        ),
        "insights": prioritized,
    }


