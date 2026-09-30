from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dashboard_model import Dashboard

async def create_dashboard(
    db: AsyncSession,
    project_id: int,
    name: str
):
    dashboard = Dashboard(
        name=name,
        project_id=project_id
    )

    db.add(dashboard)

    await db.flush()
    await db.refresh(dashboard)
    await db.commit()

    return dashboard


async def get_project_dashboards(
    db: AsyncSession,
    project_id: int
):
    result = await db.execute(
        select(Dashboard).where(
            Dashboard.project_id == project_id
        )
    )

    return result.scalars().all()