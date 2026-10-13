
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_otp_digest, verify_otp
from app.models.password_reset_otp_model import PasswordResetOTP
from app.models.user_model import User


OTP_EXPIRY_MINUTES = 5
MAX_OTP_ATTEMPTS = 5
OTP_REQUEST_COOLDOWN_SECONDS = 60


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def generate_reset_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


async def create_password_reset_otp(
    db: AsyncSession,
    user: User,
) -> str:
    now = _utc_now()

    try:
        result = await db.execute(
            select(PasswordResetOTP)
            .where(PasswordResetOTP.user_id == user.id)
            .order_by(PasswordResetOTP.created_at.desc())
            .limit(1)
        )

        latest_otp = result.scalar_one_or_none()

        if latest_otp is not None:
            created_at = _normalize_datetime(latest_otp.created_at)
            elapsed_seconds = (now - created_at).total_seconds()

            if elapsed_seconds < OTP_REQUEST_COOLDOWN_SECONDS:
                remaining_seconds = max(
                    1,
                    int(OTP_REQUEST_COOLDOWN_SECONDS - elapsed_seconds) + 1,
                )
                raise ValueError(
                    f"Please wait {remaining_seconds} seconds "
                    "before requesting another OTP"
                )

        # Invalidate previously active OTPs.
        await db.execute(
            update(PasswordResetOTP)
            .where(
                PasswordResetOTP.user_id == user.id,
                PasswordResetOTP.used.is_(False),
            )
            .values(used=True)
        )

        otp = generate_reset_otp()
        otp_digest = create_otp_digest(
            otp,
            user.id,
            "password-reset",
        )

        otp_record = PasswordResetOTP(
            user_id=user.id,
            otp_hash=otp_digest,
            expires_at=now + timedelta(minutes=OTP_EXPIRY_MINUTES),
            attempts=0,
            used=False,
        )

        db.add(otp_record)
        await db.commit()
        await db.refresh(otp_record)

        return otp

    except Exception:
        await db.rollback()
        raise


async def verify_password_reset_otp(
    db: AsyncSession,
    user: User,
    otp: str,
) -> PasswordResetOTP:
    try:
        result = await db.execute(
            select(PasswordResetOTP)
            .where(
                PasswordResetOTP.user_id == user.id,
                PasswordResetOTP.used.is_(False),
            )
            .order_by(PasswordResetOTP.created_at.desc())
            .limit(1)
            .with_for_update()
        )

        otp_record = result.scalar_one_or_none()

        if otp_record is None:
            raise ValueError("No active OTP found")

        now = _utc_now()
        expires_at = _normalize_datetime(otp_record.expires_at)

        if expires_at <= now:
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
            "password-reset",
        ):
            otp_record.attempts += 1

            if otp_record.attempts >= MAX_OTP_ATTEMPTS:
                otp_record.used = True

            attempts_exceeded = otp_record.attempts >= MAX_OTP_ATTEMPTS
            await db.commit()

            if attempts_exceeded:
                raise ValueError("Too many incorrect attempts")

            raise ValueError("Invalid OTP")

        otp_record.used = True
        await db.commit()

        return otp_record

    except ValueError:
        # Preserve intentional commits that record failed attempts or expiry.
        if db.in_transaction():
            await db.rollback()
        raise

    except Exception:
        await db.rollback()
        raise
