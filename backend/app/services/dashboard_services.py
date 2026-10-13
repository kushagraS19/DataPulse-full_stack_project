from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dashboard_model import Dashboard
from app.models.dataset_model import Dataset


async def create_dashboard(
    db: AsyncSession,
    project_id: int,
    dataset_id: int,
    name: str,
):
    try:
        # Confirm that the dataset belongs to this project.
        dataset_result = await db.execute(
            select(Dataset).where(
                Dataset.id == dataset_id,
                Dataset.project_id == project_id,
            )
        )

        dataset = dataset_result.scalar_one_or_none()

        if dataset is None:
            raise ValueError(
                "Dataset not found in the specified project"
            )

        # Reuse the existing dashboard instead of creating a duplicate.
        dashboard_result = await db.execute(
            select(Dashboard).where(
                Dashboard.dataset_id == dataset_id
            )
        )

        existing_dashboard = dashboard_result.scalar_one_or_none()

        if existing_dashboard is not None:
            return existing_dashboard

        # Create a dashboard only if the dataset has none.
        dashboard = Dashboard(
            name=name,
            project_id=project_id,
            dataset_id=dataset_id,
        )

        db.add(dashboard)
        await db.commit()
        await db.refresh(dashboard)

        return dashboard

    except Exception:
        await db.rollback()
        raise


async def get_project_dashboards(
    db: AsyncSession,
    project_id: int,
):
    result = await db.execute(
        select(Dashboard).where(
            Dashboard.project_id == project_id
        )
    )

    return result.scalars().all()