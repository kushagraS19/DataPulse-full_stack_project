import os

import pandas as pd
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_model import Dataset
from app.models.dataset_row_model import DatasetRow


async def create_dataset(
    db: AsyncSession,
    project_id: int,
    name: str,
    file_path: str,
    row_count: int = 0,
    column_count: int = 0,
    file_size: int = 0
):
    dataset = Dataset(
        name=name,
        file_path=file_path,
        project_id=project_id,
        table_name="pending",
        row_count=row_count,
        column_count=column_count,
        file_size=file_size
    )

    db.add(dataset)

    await db.flush()

    dataset.table_name = f"dataset_{dataset.id}_data"

    await db.commit()

    await db.refresh(dataset)

    return dataset


async def rename_dataset(
    db: AsyncSession,
    dataset_id: int,
    project_id: int,
    name: str
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.project_id == project_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    dataset.name = name.strip()

    await db.commit()
    await db.refresh(dataset)

    return dataset


async def get_project_datasets(
    db: AsyncSession,
    project_id: int
):
    result = await db.execute(
        select(Dataset)
        .where(
            Dataset.project_id == project_id
        )
    )

    return result.scalars().all()


async def preview_dataset(
    db: AsyncSession,
    dataset_id: int,
    project_id: int
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.project_id == project_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    try:
        df = pd.read_csv(
            dataset.file_path
        )
    except Exception as e:
        raise ValueError(
            f"Failed to read dataset: {str(e)}"
        )

    preview = df.head(10).to_dict(
        orient="records"
    )

    return {
        "dataset_id": dataset.id,
        "columns": df.columns.tolist(),
        "row_count": len(df),
        "preview": preview
    }


async def get_dataset_by_id(
    db: AsyncSession,
    dataset_id: int,
    project_id: int
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.project_id == project_id
        )
    )

    return result.scalar_one_or_none()


async def get_dataset_data(
    db: AsyncSession,
    dataset_id: int,
    project_id: int
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.project_id == project_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    try:
        df = pd.read_csv(
            dataset.file_path
        )

    except Exception as e:
        raise ValueError(
            f"Failed to read dataset: {str(e)}"
        )

    return {
        "dataset_id": dataset.id,
        "project_id": dataset.project_id,
        "name": dataset.name,
        "columns": df.columns.tolist(),
        "row_count": len(df),
        "data": df.to_dict(
            orient="records"
        )
    }


async def store_dataset_rows(
    db: AsyncSession,
    dataset_id: int
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    try:
        df = pd.read_csv(
            dataset.file_path
        )

    except Exception as e:
        raise ValueError(
            f"Failed to read dataset: {str(e)}"
        )

    rows = df.where(
        pd.notnull(df),
        None
    ).to_dict(
        orient="records"
    )

    dataset_rows = [
        DatasetRow(
            dataset_id=dataset_id,
            row_data=row
        )
        for row in rows
    ]

    db.add_all(dataset_rows)

    await db.commit()

    return {
        "dataset_id": dataset_id,
        "rows_stored": len(dataset_rows)
    }


async def create_dataset_table(
    db: AsyncSession,
    dataset_id: int,
    df: pd.DataFrame
):
    table_name = f"dataset_{dataset_id}_data"

    columns = []

    column_mapping = {}

    for column in df.columns:

        original_column = str(column)

        safe_column = (
            original_column
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        column_mapping[original_column] = safe_column

        if pd.api.types.is_integer_dtype(df[column]):

            sql_type = "BIGINT"

        elif pd.api.types.is_float_dtype(df[column]):

            sql_type = "DOUBLE PRECISION"

        elif pd.api.types.is_bool_dtype(df[column]):

            sql_type = "BOOLEAN"

        elif pd.api.types.is_datetime64_any_dtype(df[column]):

            sql_type = "TIMESTAMP"

        else:

            sql_type = "TEXT"

        columns.append(
            f'"{safe_column}" {sql_type}'
        )

    columns_sql = ", ".join(columns)

    create_table_query = text(
        f"""
        CREATE TABLE "{table_name}" (
            "_row_id" BIGSERIAL PRIMARY KEY,
            {columns_sql}
        )
        """
    )

    await db.execute(
        create_table_query
    )

    df = df.rename(
        columns=column_mapping
    )

    df = df.where(
        pd.notnull(df),
        None
    )

    column_names = list(
        df.columns
    )

    column_sql = ", ".join(
        f'"{column}"'
        for column in column_names
    )

    placeholders = ", ".join(
        f":{column}"
        for column in column_names
    )

    insert_query = text(
        f"""
        INSERT INTO "{table_name}"
        ({column_sql})
        VALUES ({placeholders})
        """
    )

    rows = df.to_dict(
        orient="records"
    )

    if rows:

        await db.execute(
            insert_query,
            rows
        )

    await db.commit()

    return {
        "table_name": table_name,
        "rows_inserted": len(rows)
    }


async def delete_dataset(
    db: AsyncSession,
    dataset_id: int,
    project_id: int
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.project_id == project_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    file_path = dataset.file_path
    table_name = dataset.table_name

    try:
        # Delete stored dataset rows first.
        await db.execute(
            text(
                """
                DELETE FROM dataset_rows
                WHERE dataset_id = :dataset_id
                """
            ),
            {
                "dataset_id": dataset_id
            }
        )

        # Drop the analytical table created for this dataset.
        if (
            table_name
            and table_name != "pending"
        ):
            await db.execute(
                text(
                    f'DROP TABLE IF EXISTS "{table_name}"'
                )
            )

        # Delete the dataset database record.
        await db.delete(dataset)

        await db.commit()

    except Exception:
        await db.rollback()
        raise

    # Remove the processed CSV file after the database
    # deletion has completed successfully.
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)

        except OSError as e:
            raise ValueError(
                f"Dataset was deleted, but the stored file could not be removed: {str(e)}"
            )

    return {
        "message": "Dataset deleted successfully",
        "dataset_id": dataset_id
    }


async def get_dataset_columns(
    db: AsyncSession,
    dataset_id: int
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    query = text(
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = :table_name
        AND column_name != '_row_id'
        ORDER BY ordinal_position
        """
    )

    result = await db.execute(
        query,
        {
            "table_name": dataset.table_name
        }
    )

    columns = result.fetchall()

    return [
        {
            "name": column.column_name,
            "data_type": column.data_type
        }
        for column in columns
    ]


async def get_dataset_column_operations(
    db: AsyncSession,
    dataset_id: int
):
    columns = await get_dataset_columns(
        db,
        dataset_id
    )

    if columns is None:
        return None

    numeric_types = {
        "bigint",
        "integer",
        "smallint",
        "numeric",
        "double precision",
        "real"
    }

    result = []

    for column in columns:

        if column["data_type"] in numeric_types:
            operations = [
                "sum",
                "average",
                "count",
                "count_distinct",
                "min",
                "max"
            ]
        else:
            operations = [
                "count",
                "count_distinct"
            ]

        result.append(
            {
                "name": column["name"],
                "data_type": column["data_type"],
                "operations": operations
            }
        )

    return result


async def get_dataset_column_statistics(
    db: AsyncSession,
    dataset_id: int
):
    dataset_result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = dataset_result.scalar_one_or_none()

    if dataset is None:
        return None

    query = text(
        """
        SELECT
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_name = :table_name
        AND column_name != '_row_id'
        ORDER BY ordinal_position
        """
    )

    result = await db.execute(
        query,
        {
            "table_name": dataset.table_name
        }
    )

    columns = result.fetchall()

    statistics = []

    for column in columns:
        column_name = column.column_name

        count_query = text(
            f'''
            SELECT
                COUNT(*) AS total_count,
                COUNT("{column_name}") AS non_null_count,
                COUNT(*) - COUNT("{column_name}") AS null_count,
                COUNT(DISTINCT "{column_name}") AS unique_count
            FROM "{dataset.table_name}"
            '''
        )

        count_result = await db.execute(
            count_query
        )

        counts = count_result.fetchone()

        total_count = counts.total_count
        non_null_count = counts.non_null_count
        null_count = counts.null_count
        unique_count = counts.unique_count

        if total_count > 0:
            missing_percentage = (
                null_count / total_count
            ) * 100
        else:
            missing_percentage = 0

        statistics.append({
            "name": column_name,
            "data_type": column.data_type,
            "total_count": total_count,
            "non_null_count": non_null_count,
            "null_count": null_count,
            "unique_count": unique_count,
            "missing_percentage": round(
                missing_percentage,
                2
            )
        })

    return statistics