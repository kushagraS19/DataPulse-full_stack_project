from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User
from app.models.workspace_model import Workspace
from app.models.project_model import Project
from app.models.dataset_model import Dataset
from app.models.dashboard_model import Dashboard
from app.models.chart_model import Chart


async def _count(db: AsyncSession, model, *conditions) -> int:
    query = select(func.count()).select_from(model)

    if conditions:
        query = query.where(*conditions)

    result = await db.execute(query)
    return result.scalar_one()


async def get_admin_overview(db: AsyncSession) -> dict:
    total_users = await _count(db, User)
    verified_users = await _count(
        db, User, User.email_verified.is_(True)
    )

    total_rows_result = await db.execute(
        select(func.coalesce(func.sum(Dataset.row_count), 0))
    )
    storage_result = await db.execute(
        select(func.coalesce(func.sum(Dataset.file_size), 0))
    )

    return {
        "total_users": total_users,
        "verified_users": verified_users,
        "unverified_users": total_users - verified_users,
        "total_workspaces": await _count(db, Workspace),
        "total_projects": await _count(db, Project),
        "total_datasets": await _count(db, Dataset),
        "total_dashboards": await _count(db, Dashboard),
        "total_charts": await _count(db, Chart),
        "total_rows": int(total_rows_result.scalar_one()),
        "storage_bytes": int(storage_result.scalar_one()),
    }


async def get_admin_users(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    search: str | None = None,
    role: str | None = None,
) -> dict:
    workspace_count = (
        select(func.count(Workspace.id))
        .where(Workspace.owner_id == User.id)
        .correlate(User)
        .scalar_subquery()
    )

    project_count = (
        select(func.count(Project.id))
        .join(Workspace, Project.workspace_id == Workspace.id)
        .where(Workspace.owner_id == User.id)
        .correlate(User)
        .scalar_subquery()
    )

    dataset_count = (
        select(func.count(Dataset.id))
        .join(Project, Dataset.project_id == Project.id)
        .join(Workspace, Project.workspace_id == Workspace.id)
        .where(Workspace.owner_id == User.id)
        .correlate(User)
        .scalar_subquery()
    )

    dashboard_count = (
        select(func.count(Dashboard.id))
        .join(Project, Dashboard.project_id == Project.id)
        .join(Workspace, Project.workspace_id == Workspace.id)
        .where(Workspace.owner_id == User.id)
        .correlate(User)
        .scalar_subquery()
    )

    chart_count = (
        select(func.count(Chart.id))
        .join(Dashboard, Chart.dashboard_id == Dashboard.id)
        .join(Project, Dashboard.project_id == Project.id)
        .join(Workspace, Project.workspace_id == Workspace.id)
        .where(Workspace.owner_id == User.id)
        .correlate(User)
        .scalar_subquery()
    )

    conditions = []

    if search and search.strip():
        search_term = f"%{search.strip()}%"
        conditions.append(
            User.name.ilike(search_term)
            | User.email.ilike(search_term)
        )

    if role:
        conditions.append(User.role == role)

    count_query = select(func.count()).select_from(User)

    if conditions:
        count_query = count_query.where(*conditions)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = select(
        User.id.label("id"),
        User.name.label("name"),
        User.email.label("email"),
        User.role.label("role"),
        User.email_verified.label("email_verified"),
        User.is_active.label("is_active"),
        User.created_at.label("created_at"),
        workspace_count.label("workspace_count"),
        project_count.label("project_count"),
        dataset_count.label("dataset_count"),
        dashboard_count.label("dashboard_count"),
        chart_count.label("chart_count"),
    )

    if conditions:
        query = query.where(*conditions)

    query = (
        query
        .order_by(User.created_at.desc(), User.id.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(query)
    items = [dict(row) for row in result.mappings().all()]

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


async def update_user_role(
    db: AsyncSession,
    user_id: int,
    new_role: str,
    admin_id: int,
):
    if new_role not in {"user", "admin"}:
        raise ValueError("Role must be 'user' or 'admin'")

    # Never allow role changes through this endpoint.
    # The designated admin remains admin, and users remain users.
    if user_id == admin_id:
        raise ValueError("You cannot change your own admin role")

    if new_role == "admin":
        raise ValueError("Promoting users to admin is disabled")

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        return None

    if user.role == "admin":
        raise ValueError("The admin role cannot be removed through this endpoint")

    # No role change is needed if the user is already a regular user.
    return user


async def set_user_active_status(
    db: AsyncSession,
    user_id: int,
    is_active: bool,
    admin_id: int,
):
    if user_id == admin_id:
        raise ValueError("You cannot change your own account status")

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        return None

    if user.role == "admin":
        raise ValueError("The admin account status cannot be changed here")

    if user.is_active == is_active:
        return user

    user.is_active = is_active

    # Revoke existing sessions when deactivating an account.
    if not is_active:
        user.token_version += 1

    try:
        await db.commit()
        await db.refresh(user)
    except Exception:
        await db.rollback()
        raise

    return user