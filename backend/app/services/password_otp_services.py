import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_otp_digest, verify_otp
from app.models.password_change_otp_model import PasswordChangeOTP
from app.models.user_model import User
from datetime import datetime, timedelta, timezone


OTP_EXPIRY_MINUTES = 5
MAX_OTP_ATTEMPTS = 5
OTP_REQUEST_COOLDOWN_SECONDS = 60

def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


async def create_password_change_otp(
    db: AsyncSession,
    user: User
) -> str:

    now = datetime.now(timezone.utc)

    # Check when the latest OTP was created
    result = await db.execute(
        select(PasswordChangeOTP)
        .where(
            PasswordChangeOTP.user_id == user.id
        )
        .order_by(
            PasswordChangeOTP.created_at.desc()
        )
        .limit(1)
    )

    latest_otp = result.scalar_one_or_none()

    if latest_otp is not None:

        # Make sure the DB timestamp is timezone-aware
        latest_created_at = latest_otp.created_at

        if latest_created_at.tzinfo is None:
            latest_created_at = latest_created_at.replace(
                tzinfo=timezone.utc
            )

        elapsed_seconds = (
            now - latest_created_at
        ).total_seconds()

        if elapsed_seconds < OTP_REQUEST_COOLDOWN_SECONDS:

            remaining_seconds = int(
                OTP_REQUEST_COOLDOWN_SECONDS - elapsed_seconds
            )

            raise ValueError(
                f"Please wait {remaining_seconds} seconds before requesting another OTP"
            )

    # Generate new OTP
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
        user.id,
        "password-change"
    )

    expires_at = (
        now +
        timedelta(minutes=OTP_EXPIRY_MINUTES)
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
        otp_record.otp_hash,
        "password-change"
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