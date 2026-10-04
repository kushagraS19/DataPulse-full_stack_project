from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace_model import Workspace


async def create_workspace(
    db: AsyncSession,
    owner_id: int,
    name: str
):
    workspace = Workspace(
        name=name,
        owner_id=owner_id
    )

    db.add(workspace)

    await db.flush()
    await db.refresh(workspace)
    await db.commit()

    return workspace


async def get_user_workspaces(
    db: AsyncSession,
    user_id: int
):
    result = await db.execute(
        select(Workspace)
        .where(
            Workspace.owner_id == user_id
        )
    )

    return result.scalars().all()


async def get_workspace_by_id(
    db: AsyncSession,
    workspace_id: int,
    owner_id: int
):
    result = await db.execute(
        select(Workspace)
        .where(
            Workspace.id == workspace_id,
            Workspace.owner_id == owner_id
        )
    )

    return result.scalar_one_or_none()


async def update_workspace(
    db: AsyncSession,
    workspace_id: int,
    owner_id: int,
    name: str
):
    workspace = await get_workspace_by_id(
        db,
        workspace_id,
        owner_id
    )

    if workspace is None:
        return None

    workspace.name = name

    await db.flush()
    await db.refresh(workspace)
    await db.commit()

    return workspace


async def delete_workspace(
    db: AsyncSession,
    workspace_id: int,
    owner_id: int
):
    workspace = await get_workspace_by_id(
        db,
        workspace_id,
        owner_id
    )

    if workspace is None:
        return None

    await db.delete(workspace)
    await db.commit()

    return workspace


