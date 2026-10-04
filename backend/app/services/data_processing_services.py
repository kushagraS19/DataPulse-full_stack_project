import pandas as pd


def process_csv(file_path: str) -> pd.DataFrame:
    """
    Read, validate, and clean a CSV file using Pandas.
    """

    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp1252"
    ]

    df = None

    for encoding in encodings:
        try:
            df = pd.read_csv(
                file_path,
                keep_default_na=True,
                encoding=encoding
            )
            break

        except UnicodeDecodeError:
            continue

        except pd.errors.EmptyDataError:
            raise ValueError(
                "CSV file contains no data"
            )

        except pd.errors.ParserError:
            raise ValueError(
                "Invalid CSV format. Please check that all rows have a consistent number of columns."
            )

        except Exception as e:
            raise ValueError(
                f"Failed to process CSV file: {str(e)}"
            )

    if df is None:
        raise ValueError(
            "CSV file encoding is not supported. Please save the file as UTF-8 and try again."
        )

    # CSV must contain at least one column
    if len(df.columns) == 0:
        raise ValueError(
            "CSV file must contain at least one column"
        )

    # CSV must contain at least one data row
    if df.empty:
        raise ValueError(
            "CSV file contains no data rows"
        )

    # Remove completely empty rows
    df = df.dropna(
        how="all"
    )

    # Remove completely empty columns
    df = df.dropna(
        axis=1,
        how="all"
    )

    if df.empty:
        raise ValueError(
            "CSV file contains no usable data"
        )

    if len(df.columns) == 0:
        raise ValueError(
            "CSV file contains no usable columns"
        )

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(
            r"[^a-z0-9_]",
            "",
            regex=True
        )
    )

    # Validate column names after cleaning
    if any(
        not column
        for column in df.columns
    ):
        raise ValueError(
            "CSV contains a column with an invalid or empty name"
        )

    
    # Handle duplicate column names
    column_counts = {}

    unique_columns = []

    for column in df.columns:

        if column not in column_counts:
            column_counts[column] = 1
            unique_columns.append(column)

        else :
            column_counts[column] += 1

            unique_columns.append(
                f"{column}_{column_counts[column]}"
            )

    df.columns = unique_columns   

    # Standardize text values
    for column in df.select_dtypes(
        include="object"
    ).columns:

        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    # Convert numeric columns
    for column in df.columns:

        if df[column].dtype == "object":

            converted_column = pd.to_numeric(
                df[column],
                errors="coerce"
            )

            non_null_values = (
                df[column].notna().sum()
            )

            converted_values = (
                converted_column.notna().sum()
            )

            if (
                non_null_values > 0
                and converted_values == non_null_values
            ):
                df[column] = converted_column

    # Detect datetime columns
    for column in df.columns:

        if df[column].dtype == "object":

            converted_column = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            non_null_values = (
                df[column].notna().sum()
            )

            converted_values = (
                converted_column.notna().sum()
            )

            if (
                non_null_values > 0
                and converted_values == non_null_values
            ):
                df[column] = converted_column

    # Handle missing values
    for column in df.columns:

        if df[column].isna().any():

            # Numeric column
            if pd.api.types.is_numeric_dtype(
                df[column]
            ):

                median_value = df[column].median()

                if pd.isna(median_value):
                    df[column] = df[column].fillna(0)

                else:
                    df[column] = df[column].fillna(
                        median_value
                    )

            # Text / categorical column
            else:

                df[column] = df[column].fillna(
                    "Unknown"
                )

    # Final safety check
    if df.isna().any().any():
        raise ValueError(
            "Dataset still contains missing values after cleaning"
        )

    return df