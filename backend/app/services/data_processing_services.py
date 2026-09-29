import pandas as pd


def process_csv(file_path: str) -> pd.DataFrame:
    """
    Read and clean a CSV file using Pandas.
    """

    try:
        df = pd.read_csv(file_path, keep_default_na=True)
        print("PROCESS CSV CALLED")
        print("FILE:", file_path)
        print("BEFORE CLEANING:")
        print(df)
        print("MISSING VALUES:")
        print(df.isna().sum())

    except Exception as e:
        raise ValueError(
            f"Failed to process CSV file: {str(e)}"
        )

    if df.empty:
        raise ValueError(
            "CSV file contains no data"
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

    # Remove duplicate rows
    df = df.drop_duplicates()

    df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace(r"[^a-z0-9_]", "", regex=True)
)

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

    for column in df.columns:

        if df[column].dtype == "object":

            converted_column = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        # Check how many values were successfully
        # converted to numeric
            non_null_values = df[column].notna().sum()
            converted_values = converted_column.notna().sum()

            if (
                non_null_values > 0
                and converted_values == non_null_values
            ):
                df[column] = converted_column



    # DETECT DATETIME COLUMNS
    for column in df.columns:

        if df[column].dtype == "object":

            converted_column = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            non_null_values = df[column].notna().sum()
            converted_values = converted_column.notna().sum()

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

    print("AFTER CLEANING:")
    print(df)
    print("MISSING VALUES AFTER CLEANING:")
    print(df.isna().sum())

    return df