import logging
import re

import pandas as pd


logger = logging.getLogger(__name__)

MAX_ROWS = 250_000
MAX_COLUMNS = 200
MAX_COLUMN_NAME_LENGTH = 63


def _make_unique_columns(columns: list[str]) -> list[str]:
    """Normalize column names and guarantee unique identifiers."""

    result = []
    used = set()

    for original in columns:
        name = str(original).strip().lower()
        name = re.sub(r"[^a-z0-9_]", "_", name)
        name = re.sub(r"_+", "_", name).strip("_")

        if not name:
            name = "column"

        name = name[:MAX_COLUMN_NAME_LENGTH]
        candidate = name
        suffix = 2

        while candidate in used:
            suffix_text = f"_{suffix}"
            candidate = (
                f"{name[:MAX_COLUMN_NAME_LENGTH - len(suffix_text)]}"
                f"{suffix_text}"
            )
            suffix += 1

        used.add(candidate)
        result.append(candidate)

    return result


def _convert_column_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convert clearly numeric or date-like text columns."""

    for column in df.columns:
        if not (
            pd.api.types.is_object_dtype(df[column])
            or pd.api.types.is_string_dtype(df[column])
        ):
            continue

        series = df[column]

        # Convert to numeric only when all non-missing values qualify.
        numeric = pd.to_numeric(series, errors="coerce")
        non_missing = series.notna().sum()

        if (
            non_missing > 0
            and numeric.notna().sum() == non_missing
        ):
            df[column] = numeric
            continue

        # Do not automatically interpret arbitrary strings or numeric
        # identifiers as dates. Require recognizable date separators.
        values = series.dropna().astype(str).str.strip()

        if values.empty:
            continue

        date_pattern = values.str.contains(
            r"[-/]",
            regex=True,
        )

        if date_pattern.mean() < 0.9:
            continue

        # Only convert when at least 90% of non-missing values parse.
        # Mixed text/date columns remain text.
        try:
            converted = pd.to_datetime(
                series,
                errors="coerce",
                format="mixed",
                utc=False,
            )

            valid_count = converted.notna().sum()

            if valid_count / non_missing >= 0.9:
                df[column] = converted

        except (ValueError, TypeError, OverflowError):
            logger.debug(
                "Date conversion skipped for column %s",
                column,
            )

    return df


def process_csv(file_path: str) -> pd.DataFrame:
    """
    Read, validate, and clean a CSV file.

    Limits input size by row and column count to reduce memory-exhaustion
    risk. The upload endpoint should also enforce a file-size limit.
    """

    encodings = ("utf-8", "utf-8-sig", "cp1252")
    df = None

    for encoding in encodings:
        try:
            # Read one extra row so oversized files are detected rather
            # than silently truncated.
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                keep_default_na=True,
                nrows=MAX_ROWS + 1,
                low_memory=False,
                on_bad_lines="error",
            )
            break

        except UnicodeDecodeError:
            continue

        except pd.errors.EmptyDataError as exc:
            raise ValueError(
                "CSV file contains no data."
            ) from exc

        except pd.errors.ParserError as exc:
            raise ValueError(
                "Invalid CSV format. Check that rows have a consistent "
                "number of columns and valid quoting."
            ) from exc

        except (OSError, PermissionError) as exc:
            logger.warning("Unable to read uploaded CSV: %s", exc)
            raise ValueError(
                "Unable to read the CSV file."
            ) from exc

        except Exception as exc:
            logger.exception("Unexpected CSV processing error")
            raise ValueError(
                "Failed to process CSV file."
            ) from exc

    if df is None:
        raise ValueError(
            "Unsupported CSV encoding. Save the file as UTF-8 and retry."
        )

    if len(df) > MAX_ROWS:
        raise ValueError(
            f"CSV exceeds the maximum of {MAX_ROWS:,} data rows."
        )

    if len(df.columns) == 0:
        raise ValueError(
            "CSV must contain at least one column."
        )

    if len(df.columns) > MAX_COLUMNS:
        raise ValueError(
            f"CSV cannot contain more than {MAX_COLUMNS} columns."
        )

    if df.empty:
        raise ValueError(
            "CSV contains no data rows."
        )

    # Remove rows and columns that contain only missing values.
    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")

    if df.empty or len(df.columns) == 0:
        raise ValueError(
            "CSV contains no usable data."
        )

    # Remove duplicate rows.
    df = df.drop_duplicates()

    # Normalize column names and handle collisions safely.
    df.columns = _make_unique_columns(list(df.columns))

    # Strip text and convert empty strings to missing values without
    # converting actual missing values into the string "nan".
    for column in df.select_dtypes(include=["object", "string"]).columns:
        series = df[column].map(
            lambda value: value.strip()
            if isinstance(value, str)
            else value
        )

        df[column] = series.replace("", pd.NA)

    # Convert clearly numeric and recognizable date-like columns.
    df = _convert_column_types(df)

    # Impute missing values.
    for column in df.columns:
        if not df[column].isna().any():
            continue

        if pd.api.types.is_numeric_dtype(df[column]):
            median_value = df[column].median()

            if pd.isna(median_value):
                df[column] = df[column].fillna(0)
            else:
                df[column] = df[column].fillna(median_value)

        elif pd.api.types.is_datetime64_any_dtype(df[column]):
            # Missing dates should remain missing rather than being
            # replaced with a fabricated date.
            continue

        else:
            df[column] = df[column].fillna("Unknown")

    # Final validation.
    if df.empty or len(df.columns) == 0:
        raise ValueError(
            "CSV contains no usable data after cleaning."
        )

    return df.reset_index(drop=True)