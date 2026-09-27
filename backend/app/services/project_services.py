from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_model import Project

async def create_project(
        db : AsyncSession,
        workspace_id : int,
        name : str
):
    project = Project(
        name=name,
        workspace_id=workspace_id
    )

    db.add(project)

    await db.flush()
    await db.refresh(project)

    await db.commit()

    return project


async def get_workspace_projects(
        db : AsyncSession,
        workspace_id : int
):
    result = await db.execute(
        select(Project)
        .where(
            Project.workspace_id == workspace_id
        )
    )

    return result.scalars().all()


