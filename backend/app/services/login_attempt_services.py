
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, case
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.login_attempt_model import LoginAttempt


MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


async def get_login_attempt(
    db: AsyncSession,
    email: str,
    ip_address: str,
):
    result = await db.execute(
        select(LoginAttempt).where(
            LoginAttempt.email == email,
            LoginAttempt.ip_address == ip_address,
        )
    )

    return result.scalar_one_or_none()


async def is_login_locked(
    db: AsyncSession,
    email: str,
    ip_address: str,
) -> bool:
    result = await db.execute(
        select(LoginAttempt)
        .where(
            LoginAttempt.email == email,
            LoginAttempt.ip_address == ip_address,
        )
        .with_for_update()
    )

    attempt = result.scalar_one_or_none()

    if attempt is None or attempt.locked_until is None:
        return False

    locked_until = attempt.locked_until

    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(
            tzinfo=timezone.utc
        )

    if locked_until <= datetime.now(timezone.utc):
        attempt.locked_until = None
        attempt.failed_attempts = 0
        await db.commit()
        return False

    await db.commit()
    return True


async def record_failed_login(
    db: AsyncSession,
    email: str,
    ip_address: str,
):
    now = datetime.now(timezone.utc)
    lockout_until = now + timedelta(
        minutes=LOCKOUT_MINUTES
    )

    statement = insert(LoginAttempt).values(
        email=email,
        ip_address=ip_address,
        failed_attempts=1,
        locked_until=None,
        updated_at=now,
    )

    statement = statement.on_conflict_do_update(
        constraint="uq_login_attempt_email_ip",
        set_={
            "failed_attempts": (
                LoginAttempt.failed_attempts + 1
            ),
            "locked_until": case(
                (
                    LoginAttempt.failed_attempts + 1
                    >= MAX_FAILED_ATTEMPTS,
                    lockout_until,
                ),
                else_=LoginAttempt.locked_until,
            ),
            "updated_at": now,
        },
    )

    try:
        await db.execute(statement)
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return await get_login_attempt(
        db,
        email,
        ip_address,
    )


async def reset_login_attempts(
    db: AsyncSession,
    email: str,
    ip_address: str,
):
    attempt = await get_login_attempt(
        db,
        email,
        ip_address,
    )

    if attempt is None:
        return

    attempt.failed_attempts = 0
    attempt.locked_until = None

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
