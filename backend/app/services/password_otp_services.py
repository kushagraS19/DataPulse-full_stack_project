import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_otp_digest, verify_otp
from app.models.password_change_otp_model import PasswordChangeOTP
from app.models.user_model import User


OTP_EXPIRY_MINUTES = 5
MAX_OTP_ATTEMPTS = 5


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


async def create_password_change_otp(
    db: AsyncSession,
    user: User
) -> str:

    otp = generate_otp()

    # Invalidate previous active OTPs
    await db.execute(
        update(PasswordChangeOTP)
        .where(
            PasswordChangeOTP.user_id == user.id,
            PasswordChangeOTP.used.is_(False)
        )
        .values(used=True)
    )

    otp_digest = create_otp_digest(
        otp,
        user.id
    )

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=OTP_EXPIRY_MINUTES)
    )

    otp_record = PasswordChangeOTP(
        user_id=user.id,
        otp_hash=otp_digest,
        expires_at=expires_at,
        attempts=0,
        used=False
    )

    db.add(otp_record)

    await db.commit()
    await db.refresh(otp_record)

    return otp

async def verify_password_change_otp(
    db: AsyncSession,
    user: User,
    otp: str
):
    result = await db.execute(
        select(PasswordChangeOTP)
        .where(
            PasswordChangeOTP.user_id == user.id,
            PasswordChangeOTP.used.is_(False)
        )
        .order_by(
            PasswordChangeOTP.created_at.desc()
        )
        .limit(1)
        .with_for_update()
    )

    otp_record = result.scalar_one_or_none()

    if otp_record is None:
        raise ValueError("No active OTP found")

    now = datetime.now(timezone.utc)

    if otp_record.expires_at <= now:
        otp_record.used = True

        await db.commit()

        raise ValueError("OTP has expired")

    if otp_record.attempts >= MAX_OTP_ATTEMPTS:
        otp_record.used = True

        await db.commit()

        raise ValueError("Too many incorrect attempts")

    if not verify_otp(
        otp,
        user.id,
        otp_record.otp_hash
    ):
        otp_record.attempts += 1

        if otp_record.attempts >= MAX_OTP_ATTEMPTS:
            otp_record.used = True

        await db.commit()

        raise ValueError("Invalid OTP")

    # OTP is valid
    otp_record.used = True

    await db.commit()

    return otp_record