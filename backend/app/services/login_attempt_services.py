from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.login_attempt_model import LoginAttempt


MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15

async def get_login_attempt(
        db : AsyncSession,
        email : str,
        ip_address : str
):
    result = await db.execute(
        select(LoginAttempt)
        .where(
            LoginAttempt.email == email,
            LoginAttempt.ip_address == ip_address
        )
    )

    return result.scalar_one_or_none()

async def is_login_locked(
        db : AsyncSession,
        email : str,
        ip_address : str
) -> bool:
    attempts = await get_login_attempt(
        db,
        email,
        ip_address
    )

    if attempts is None:
        return False

    if attempts.locked_until is None:
        return False

    now = datetime.now(timezone.utc)

    if attempts.locked_until <= now:
        attempts.locked_until = None
        attempts.failed_attempts = 0

        await db.commit()

        return False

    return True



async def record_failed_login(
    db: AsyncSession,
    email: str,
    ip_address: str
):
    attempt = await get_login_attempt(
        db,
        email,
        ip_address
    )

    if attempt is None:
        attempt = LoginAttempt(
            email=email,
            ip_address=ip_address,
            failed_attempts=1
        )

        db.add(attempt)

    else:
        attempt.failed_attempts += 1

    if attempt.failed_attempts >= MAX_FAILED_ATTEMPTS:
        attempt.locked_until = (
            datetime.now(timezone.utc)
            + timedelta(minutes=LOCKOUT_MINUTES)
        )

    await db.commit()

    return attempt


async def reset_login_attempts(
        db : AsyncSession,
        email : str,
        ip_address : str
):
    attempt = await get_login_attempt(
        db,
        email,
        ip_address
    )

    if attempt is None:
        return 

    attempt.failed_attempts = 0
    attempt.locked_until = None

    await db.commit()