from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_model import Dataset

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
