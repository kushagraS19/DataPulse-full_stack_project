from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log_model import AuditLog


async def create_audit_log(
    db: AsyncSession,
    admin_id: int | None,
    action: str,
    target_user_id: int | None = None,
    details: dict | None = None,
) -> AuditLog:
    log = AuditLog(
        admin_id=admin_id,
        action=action,
        target_user_id=target_user_id,
        details=details,
    )

    db.add(log)

    try:
        await db.commit()
        await db.refresh(log)
    except Exception:
        await db.rollback()
        raise

    return log


async def get_audit_logs(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
) -> list[AuditLog]:
    query = (
        select(AuditLog)
        .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(query)
    return list(result.scalars().all())