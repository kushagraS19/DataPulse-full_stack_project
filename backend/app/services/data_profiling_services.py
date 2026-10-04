from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _serialize_value(value: Any) -> Any:
    """
    Convert Pandas/NumPy values into JSON-safe Python values.
    """
    if pd.isna(value):
        return None

    if isinstance(value, (np.integer,)):
        return int(value)

    if isinstance(value, (np.floating,)):
        return float(value)

    if isinstance(value, (np.bool_,)):
        return bool(value)

    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()

    return value


def _get_data_type(series: pd.Series) -> str:
    """
    Determine the practical data type of a column.
    """
    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    if pd.api.types.is_string_dtype(series):
        return "text"

    return "other"


def _get_data_type_confidence(series: pd.Series) -> float:
    """
    Estimate how confidently a column belongs to its detected type.

    The score represents the percentage of non-null values
    that are compatible with the detected type.
    """
    non_null = series.dropna()

    if non_null.empty:
        return 0.0

    data_type = _get_data_type(series)

    if data_type == "numeric":
        return 1.0

    if data_type == "boolean":
        return 1.0

    if data_type == "datetime":
        return 1.0

    if data_type == "text":
        return 1.0

    return 0.5


def _calculate_outliers(series: pd.Series) -> dict[str, Any]:
    """
    Detect numerical outliers using the IQR method.
    """
    numeric_series = pd.to_numeric(series, errors="coerce").dropna()

    if numeric_series.empty:
        return {
            "count": 0,
            "percentage": 0.0,
            "lower_bound": None,
            "upper_bound": None,
        }

    q1 = float(numeric_series.quantile(0.25))
    q3 = float(numeric_series.quantile(0.75))
    iqr = q3 - q1

    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)

    outliers = numeric_series[
        (numeric_series < lower_bound)
        | (numeric_series > upper_bound)
    ]

    count = int(len(outliers))
    total = int(len(numeric_series))

    return {
        "count": count,
        "percentage": round((count / total) * 100, 2) if total else 0.0,
        "lower_bound": _serialize_value(lower_bound),
        "upper_bound": _serialize_value(upper_bound),
    }


def _calculate_date_profile(series: pd.Series) -> dict[str, Any]:
    """
    Calculate useful statistics for datetime columns.
    """
    datetime_series = pd.to_datetime(series, errors="coerce").dropna()

    if datetime_series.empty:
        return {
            "min": None,
            "max": None,
            "range_days": None,
            "frequency": None,
        }

    minimum = datetime_series.min()
    maximum = datetime_series.max()

    range_days = int((maximum - minimum).days)

    frequency = None

    if len(datetime_series) >= 2:
        sorted_dates = datetime_series.sort_values()
        differences = sorted_dates.diff().dropna()

        if not differences.empty:
            median_difference = differences.median()

            if median_difference <= pd.Timedelta(days=1):
                frequency = "daily"
            elif median_difference <= pd.Timedelta(days=7):
                frequency = "weekly"
            elif median_difference <= pd.Timedelta(days=31):
                frequency = "monthly"
            elif median_difference <= pd.Timedelta(days=92):
                frequency = "quarterly"
            else:
                frequency = "yearly"

    return {
        "min": minimum.isoformat(),
        "max": maximum.isoformat(),
        "range_days": range_days,
        "frequency": frequency,
    }


def _calculate_numeric_profile(series: pd.Series) -> dict[str, Any]:
    """
    Calculate statistical information for a numerical column.
    """
    numeric_series = pd.to_numeric(series, errors="coerce").dropna()

    if numeric_series.empty:
        return {
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
            "std": None,
            "quantiles": {
                "25": None,
                "50": None,
                "75": None,
            },
            "outliers": {
                "count": 0,
                "percentage": 0.0,
                "lower_bound": None,
                "upper_bound": None,
            },
        }

    quantiles = numeric_series.quantile(
        [0.25, 0.50, 0.75]
    )

    return {
        "min": _serialize_value(numeric_series.min()),
        "max": _serialize_value(numeric_series.max()),
        "mean": _serialize_value(numeric_series.mean()),
        "median": _serialize_value(numeric_series.median()),
        "std": _serialize_value(numeric_series.std()),
        "quantiles": {
            "25": _serialize_value(quantiles.loc[0.25]),
            "50": _serialize_value(quantiles.loc[0.50]),
            "75": _serialize_value(quantiles.loc[0.75]),
        },
        "outliers": _calculate_outliers(numeric_series),
    }


def _calculate_column_profile(
    series: pd.Series,
    total_rows: int,
) -> dict[str, Any]:
    """
    Generate a complete profile for a single column.
    """
    column_name = str(series.name)

    missing_count = int(series.isna().sum())
    non_null_count = int(series.notna().sum())
    unique_count = int(series.nunique(dropna=True))

    missing_percentage = (
        (missing_count / total_rows) * 100
        if total_rows
        else 0.0
    )

    unique_percentage = (
        (unique_count / non_null_count) * 100
        if non_null_count
        else 0.0
    )

    data_type = _get_data_type(series)

    is_constant = unique_count <= 1 and non_null_count > 0

    is_high_cardinality = (
        non_null_count > 0
        and unique_percentage >= 90
        and unique_count > 20
    )

    profile = {
        "column": column_name,
        "data_type": data_type,
        "data_type_confidence": round(
            _get_data_type_confidence(series),
            2,
        ),
        "total_count": total_rows,
        "non_null_count": non_null_count,
        "missing_count": missing_count,
        "missing_percentage": round(
            missing_percentage,
            2,
        ),
        "unique_count": unique_count,
        "unique_percentage": round(
            unique_percentage,
            2,
        ),
        "is_constant": is_constant,
        "is_high_cardinality": is_high_cardinality,
    }

    if data_type == "numeric":
        profile["statistics"] = _calculate_numeric_profile(series)

    elif data_type == "datetime":
        profile["date_profile"] = _calculate_date_profile(series)
        
    elif data_type == "text":
        value_counts = (
            series.dropna()
            .astype(str)
            .value_counts()
            .head(10)
        )

        total_non_null = int(series.notna().sum())

        profile["categorical_profile"] = {
            "top_values": [
                {
                    "value": str(value),
                    "count": int(count),
                    "percentage": round(
                        (int(count) / total_non_null) * 100,
                        2,
                    ) if total_non_null else 0.0,
                }
                for value, count in value_counts.items()
            ]
        }

    return profile


def calculate_duplicate_rows(df: pd.DataFrame) -> dict[str, Any]:
    """
    Calculate duplicate-row statistics.
    """
    total_rows = len(df)

    if total_rows == 0:
        return {
            "count": 0,
            "percentage": 0.0,
        }

    duplicate_count = int(
        df.duplicated(keep="first").sum()
    )

    return {
        "count": duplicate_count,
        "percentage": round(
            (duplicate_count / total_rows) * 100,
            2,
        ),
    }


def calculate_dataset_summary(df: pd.DataFrame) -> dict[str, Any]:
    """
    Calculate high-level dataset statistics.
    """
    row_count = int(len(df))
    column_count = int(len(df.columns))

    numeric_columns = [
        str(column)
        for column in df.select_dtypes(
            include=np.number
        ).columns
    ]

    datetime_columns = [
        str(column)
        for column in df.select_dtypes(
            include=["datetime", "datetimetz"]
        ).columns
    ]

    text_columns = [
        str(column)
        for column in df.select_dtypes(
            include=["object", "string"]
        ).columns
    ]

    return {
        "row_count": row_count,
        "column_count": column_count,
        "numeric_columns": numeric_columns,
        "datetime_columns": datetime_columns,
        "text_columns": text_columns,
        "duplicate_rows": calculate_duplicate_rows(df),
    }


def profile_dataset(df: pd.DataFrame) -> dict[str, Any]:
    """
    Generate the complete analytical profile for a dataset.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "profile_dataset expects a Pandas DataFrame"
        )

    if df.empty:
        raise ValueError(
            "Cannot profile an empty dataset"
        )

    summary = calculate_dataset_summary(df)

    columns = [
        _calculate_column_profile(
            df[column],
            len(df),
        )
        for column in df.columns
    ]

    return {
        "summary": summary,
        "columns": columns,
    }