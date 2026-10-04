from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_model import Project
from app.models.workspace_model import Workspace


async def create_project(
    db: AsyncSession,
    workspace_id: int,
    name: str
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
    db: AsyncSession,
    workspace_id: int
):
    result = await db.execute(
        select(Project)
        .where(
            Project.workspace_id == workspace_id
        )
    )

    return result.scalars().all()


async def get_project_by_id(
    db: AsyncSession,
    project_id: int,
    workspace_id: int
):
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.workspace_id == workspace_id
        )
    )

    return result.scalar_one_or_none()


async def get_project_by_id_for_user(
    db: AsyncSession,
    project_id: int,
    user_id: int
):
    result = await db.execute(
        select(Project)
        .join(
            Workspace,
            Project.workspace_id == Workspace.id
        )
        .where(
            Project.id == project_id,
            Workspace.owner_id == user_id
        )
    )

    return result.scalar_one_or_none()


async def update_project(
    db: AsyncSession,
    project_id: int,
    workspace_id: int,
    name: str
):
    project = await get_project_by_id(
        db,
        project_id,
        workspace_id
    )

    if project is None:
        return None

    project.name = name

    await db.flush()
    await db.refresh(project)

    await db.commit()

    return project


async def delete_project(
    db: AsyncSession,
    project_id: int,
    user_id: int
):
    project = await get_project_by_id_for_user(
        db,
        project_id,
        user_id
    )

    if project is None:
        return None

    await db.delete(project)
    await db.commit()

    return project