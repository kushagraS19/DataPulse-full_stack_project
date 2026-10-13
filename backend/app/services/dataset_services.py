import os
import re
from datetime import date, datetime

import pandas as pd
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_model import Dataset
from app.models.dataset_row_model import DatasetRow
from app.models.dashboard_model import Dashboard


def _quote_identifier(identifier: str) -> str:
    """Safely quote a PostgreSQL identifier."""
    return '"' + str(identifier).replace('"', '""') + '"'


def _safe_dataset_file_path(file_path: str) -> str:
    """
    Resolve a dataset CSV and restrict access to uploads/processed.
    """
    processed_root = os.path.realpath(
        os.path.join(os.getcwd(), "uploads", "processed")
    )

    candidate = os.path.realpath(
        file_path
        if os.path.isabs(file_path)
        else os.path.join(os.getcwd(), file_path)
    )

    try:
        inside_root = (
            os.path.commonpath([processed_root, candidate])
            == processed_root
        )
    except ValueError:
        inside_root = False

    if (
        not inside_root
        or not candidate.lower().endswith(".csv")
        or not os.path.isfile(candidate)
    ):
        raise ValueError(
            "Dataset file must be an existing CSV inside uploads/processed"
        )

    return candidate


def _safe_column_names(columns) -> dict:
    """Create unique, predictable SQL column identifiers."""
    mapping = {}
    used = set()

    for original in columns:
        original_name = str(original)

        base = re.sub(
            r"[^a-zA-Z0-9_]+",
            "_",
            original_name.strip().lower(),
        ).strip("_")

        if not base:
            base = "column"

        if base[0].isdigit():
            base = f"col_{base}"

        candidate = base[:55]
        suffix = 2

        while candidate in used or candidate == "_row_id":
            suffix_text = f"_{suffix}"
            candidate = (
                f"{base[:63 - len(suffix_text)]}{suffix_text}"
            )
            suffix += 1

        used.add(candidate)
        mapping[original] = candidate

    return mapping


async def create_dataset(
    db: AsyncSession,
    project_id: int,
    name: str,
    file_path: str,
    row_count: int = 0,
    column_count: int = 0,
    file_size: int = 0,
):
    try:
        resolved_path = _safe_dataset_file_path(file_path)
        stored_path = os.path.relpath(
            resolved_path,
            os.getcwd(),
        )

        dataset = Dataset(
            name=name.strip(),
            file_path=stored_path,
            project_id=project_id,
            table_name="pending",
            row_count=row_count,
            column_count=column_count,
            file_size=file_size,
        )

        db.add(dataset)
        await db.flush()

        dataset.table_name = f"dataset_{dataset.id}_data"

        dashboard = Dashboard(
            name=f"{name.strip()} Dashboard",
            project_id=project_id,
            dataset_id=dataset.id,
        )

        db.add(dashboard)

        await db.commit()
        await db.refresh(dataset)

        return dataset

    except Exception:
        await db.rollback()
        raise


async def rename_dataset(
    db: AsyncSession,
    dataset_id: int,
    project_id: int,
    name: str,
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.project_id == project_id,
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
    project_id: int,
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.project_id == project_id
        )
    )

    return result.scalars().all()


async def preview_dataset(
    db: AsyncSession,
    dataset_id: int,
    project_id: int,
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.project_id == project_id,
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    try:
        file_path = _safe_dataset_file_path(dataset.file_path)
        df = pd.read_csv(file_path)

    except Exception as exc:
        raise ValueError(
            f"Failed to read dataset: {exc}"
        ) from exc

    return {
        "dataset_id": dataset.id,
        "columns": df.columns.tolist(),
        "row_count": len(df),
        "preview": df.head(10).to_dict(orient="records"),
    }


async def get_dataset_by_id(
    db: AsyncSession,
    dataset_id: int,
    project_id: int,
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.project_id == project_id,
        )
    )

    return result.scalar_one_or_none()


async def get_dataset_data(
    db: AsyncSession,
    dataset_id: int,
    project_id: int,
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.project_id == project_id,
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    try:
        file_path = _safe_dataset_file_path(dataset.file_path)
        df = pd.read_csv(file_path)

    except Exception as exc:
        raise ValueError(
            f"Failed to read dataset: {exc}"
        ) from exc

    return {
        "dataset_id": dataset.id,
        "project_id": dataset.project_id,
        "name": dataset.name,
        "columns": df.columns.tolist(),
        "row_count": len(df),
        "data": df.to_dict(orient="records"),
    }


async def store_dataset_rows(
    db: AsyncSession,
    dataset_id: int,
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
        file_path = _safe_dataset_file_path(dataset.file_path)
        df = pd.read_csv(file_path)

    except Exception as exc:
        raise ValueError(
            f"Failed to read dataset: {exc}"
        ) from exc

    rows = df.astype(object).where(
        pd.notnull(df),
        None,
    ).to_dict(orient="records")

    dataset_rows = [
        DatasetRow(
            dataset_id=dataset_id,
            row_data=row,
        )
        for row in rows
    ]

    try:
        db.add_all(dataset_rows)
        await db.commit()

    except Exception:
        await db.rollback()
        raise

    return {
        "dataset_id": dataset_id,
        "rows_stored": len(dataset_rows),
    }


async def create_dataset_table(
    db: AsyncSession,
    dataset_id: int,
    df: pd.DataFrame,
):
    if dataset_id <= 0:
        raise ValueError("Invalid dataset id")

    table_name = f"dataset_{dataset_id}_data"

    column_mapping = _safe_column_names(df.columns)
    renamed_df = df.rename(columns=column_mapping)

    sql_types = []

    for original_column in df.columns:
        safe_column = column_mapping[original_column]

        if pd.api.types.is_bool_dtype(df[original_column]):
            sql_type = "BOOLEAN"

        elif pd.api.types.is_integer_dtype(df[original_column]):
            sql_type = "BIGINT"

        elif pd.api.types.is_float_dtype(df[original_column]):
            sql_type = "DOUBLE PRECISION"

        elif pd.api.types.is_datetime64_any_dtype(
            df[original_column]
        ):
            sql_type = "TIMESTAMP"

        else:
            sql_type = "TEXT"

        sql_types.append(
            f"{_quote_identifier(safe_column)} {sql_type}"
        )

    definitions = [
        '"_row_id" BIGSERIAL PRIMARY KEY',
        *sql_types,
    ]

    create_query = text(
        f"""
        CREATE TABLE {_quote_identifier(table_name)}
        ({", ".join(definitions)})
        """
    )

    try:
        await db.execute(create_query)

        renamed_df = renamed_df.astype(object).where(
            pd.notnull(renamed_df),
            None,
        )

        column_names = list(renamed_df.columns)
        rows = renamed_df.to_dict(orient="records")

        if column_names and rows:
            column_sql = ", ".join(
                _quote_identifier(column)
                for column in column_names
            )

            bind_names = [
                f"v{i}" for i in range(len(column_names))
            ]

            placeholders = ", ".join(
                f":{name}" for name in bind_names
            )

            insert_query = text(
                f"""
                INSERT INTO {_quote_identifier(table_name)}
                ({column_sql})
                VALUES ({placeholders})
                """
            )

            parameters = [
                {
                    bind_names[i]: row.get(column_names[i])
                    for i in range(len(column_names))
                }
                for row in rows
            ]

            await db.execute(insert_query, parameters)

        await db.commit()

        return {
            "table_name": table_name,
            "rows_inserted": len(rows),
        }

    except Exception:
        await db.rollback()
        raise


async def delete_dataset(
    db: AsyncSession,
    dataset_id: int,
    project_id: int,
):
    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.project_id == project_id,
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return None

    table_name = dataset.table_name
    safe_file_to_delete = None

    if dataset.file_path:
        try:
            safe_file_to_delete = _safe_dataset_file_path(
                dataset.file_path
            )
        except ValueError:
            # Never delete files outside the managed directory.
            safe_file_to_delete = None

    try:
        await db.execute(
            text(
                """
                DELETE FROM dataset_rows
                WHERE dataset_id = :dataset_id
                """
            ),
            {"dataset_id": dataset_id},
        )

        if table_name and table_name != "pending":
            if not re.fullmatch(
                r"dataset_[0-9]+_data",
                table_name,
            ):
                raise ValueError("Invalid dataset table name")

            await db.execute(
                text(
                    f"DROP TABLE IF EXISTS "
                    f"{_quote_identifier(table_name)}"
                )
            )

        await db.delete(dataset)
        await db.commit()

    except Exception:
        await db.rollback()
        raise

    if safe_file_to_delete:
        try:
            os.remove(safe_file_to_delete)

        except OSError as exc:
            raise ValueError(
                "Dataset was deleted, but the stored file "
                f"could not be removed: {exc}"
            ) from exc

    return {
        "message": "Dataset deleted successfully",
        "dataset_id": dataset_id,
    }


async def get_dataset_columns(
    db: AsyncSession,
    dataset_id: int,
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
        WHERE table_schema = current_schema()
          AND table_name = :table_name
          AND column_name <> '_row_id'
        ORDER BY ordinal_position
        """
    )

    result = await db.execute(
        query,
        {"table_name": dataset.table_name},
    )

    return [
        {
            "name": column.column_name,
            "data_type": column.data_type,
        }
        for column in result.fetchall()
    ]


async def detect_text_date_columns(
    db: AsyncSession,
    dataset_id: int,
    sample_size: int = 200,
    threshold: float = 0.90,
) -> list[str]:
    """Detect text columns whose sampled values are valid ISO dates."""

    sample_size = max(5, min(sample_size, 1000))
    threshold = max(0.0, min(threshold, 1.0))

    result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = result.scalar_one_or_none()

    if dataset is None:
        return []

    columns = await get_dataset_columns(db, dataset_id)

    if columns is None:
        return []

    text_types = {
        "text",
        "character varying",
        "character",
        "varchar",
    }

    def is_valid_date(value: str) -> bool:
        value = value.strip()

        if not value:
            return False

        try:
            datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
            return True

        except ValueError:
            try:
                date.fromisoformat(value)
                return True

            except ValueError:
                return False

    table = _quote_identifier(dataset.table_name)
    date_columns = []

    for column in columns:
        if column["data_type"].lower() not in text_types:
            continue

        quoted_column = _quote_identifier(column["name"])

        query = text(
            f"""
            SELECT {quoted_column}
            FROM {table}
            WHERE {quoted_column} IS NOT NULL
              AND BTRIM({quoted_column}) <> ''
            LIMIT :sample_size
            """
        )

        result = await db.execute(
            query,
            {"sample_size": sample_size},
        )

        values = [
            row[0]
            for row in result.fetchall()
            if isinstance(row[0], str)
        ]

        if len(values) < 5:
            continue

        valid_count = sum(
            is_valid_date(value)
            for value in values
        )

        if valid_count / len(values) >= threshold:
            date_columns.append(column["name"])

    return date_columns


async def get_dataset_column_operations(
    db: AsyncSession,
    dataset_id: int,
):
    columns = await get_dataset_columns(
        db,
        dataset_id,
    )

    if columns is None:
        return None

    numeric_types = {
        "bigint",
        "integer",
        "smallint",
        "numeric",
        "double precision",
        "real",
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
                "max",
            ]
        else:
            operations = [
                "count",
                "count_distinct",
            ]

        result.append(
            {
                "name": column["name"],
                "data_type": column["data_type"],
                "operations": operations,
            }
        )

    return result


async def get_dataset_column_statistics(
    db: AsyncSession,
    dataset_id: int,
):
    dataset_result = await db.execute(
        select(Dataset).where(
            Dataset.id == dataset_id
        )
    )

    dataset = dataset_result.scalar_one_or_none()

    if dataset is None:
        return None

    table_name = dataset.table_name

    if not re.fullmatch(
        r"dataset_[0-9]+_data",
        table_name or "",
    ):
        raise ValueError("Invalid dataset table name")

    columns_result = await db.execute(
        text(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = current_schema()
              AND table_name = :table_name
              AND column_name <> '_row_id'
            ORDER BY ordinal_position
            """
        ),
        {"table_name": table_name},
    )

    columns = columns_result.fetchall()
    statistics = []
    quoted_table = _quote_identifier(table_name)

    for column in columns:
        quoted_column = _quote_identifier(
            column.column_name
        )

        count_query = text(
            f"""
            SELECT COUNT(*) AS total_count,
                   COUNT({quoted_column}) AS non_null_count,
                   COUNT(*) - COUNT({quoted_column}) AS null_count,
                   COUNT(DISTINCT {quoted_column}) AS unique_count
            FROM {quoted_table}
            """
        )

        counts = (
            await db.execute(count_query)
        ).fetchone()

        total_count = counts.total_count
        null_count = counts.null_count

        missing_percentage = (
            null_count / total_count * 100
            if total_count
            else 0
        )

        statistics.append(
            {
                "name": column.column_name,
                "data_type": column.data_type,
                "total_count": total_count,
                "non_null_count": counts.non_null_count,
                "null_count": null_count,
                "unique_count": counts.unique_count,
                "missing_percentage": round(
                    missing_percentage,
                    2,
                ),
            }
        )

    return statistics