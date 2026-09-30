from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_model import Dataset

import pandas as pd

async def create_dataset(
        db : AsyncSession,
        project_id : int,
        name : str,
        file_path : str
):
    dataset = Dataset(
        name=name,
        file_path=file_path,
        project_id=project_id
    )

    db.add(dataset)

    await db.flush()
    await db.refresh(dataset)

    await db.commit()

    return dataset


async def get_project_datasets(
        db : AsyncSession,
        project_id : int
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