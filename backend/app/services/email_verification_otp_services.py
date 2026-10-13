
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_otp_digest, verify_otp
from app.models.email_verification_otp_model import EmailVerificationOTP
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


def generate_email_verification_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


async def create_email_verification_otp(
    db: AsyncSession,
    user: User,
) -> str:
    try:
        # Serialize OTP creation requests for this user.
        result = await db.execute(
            select(User)
            .where(User.id == user.id)
            .with_for_update()
        )
        locked_user = result.scalar_one_or_none()

        if locked_user is None:
            raise ValueError("User not found")

        if locked_user.email_verified:
            raise ValueError("Email is already verified")

        now = _utc_now()

        result = await db.execute(
            select(EmailVerificationOTP)
            .where(EmailVerificationOTP.user_id == locked_user.id)
            .order_by(EmailVerificationOTP.created_at.desc())
            .limit(1)
        )
        latest_otp = result.scalar_one_or_none()

        if latest_otp is not None:
            created_at = _normalize_datetime(latest_otp.created_at)
            elapsed = (now - created_at).total_seconds()

            if elapsed < OTP_REQUEST_COOLDOWN_SECONDS:
                remaining = max(
                    1,
                    int(OTP_REQUEST_COOLDOWN_SECONDS - elapsed) + 1,
                )
                raise ValueError(
                    f"Please wait {remaining} seconds "
                    "before requesting another OTP"
                )

        # Invalidate previous active OTPs.
        await db.execute(
            update(EmailVerificationOTP)
            .where(
                EmailVerificationOTP.user_id == locked_user.id,
                EmailVerificationOTP.used.is_(False),
            )
            .values(used=True)
        )

        otp = generate_email_verification_otp()
        otp_hash = create_otp_digest(
            otp,
            locked_user.id,
            "email-verification",
        )

        verification_otp = EmailVerificationOTP(
            user_id=locked_user.id,
            otp_hash=otp_hash,
            expires_at=now + timedelta(minutes=OTP_EXPIRY_MINUTES),
            attempts=0,
            used=False,
        )

        db.add(verification_otp)
        await db.commit()

        return otp

    except Exception:
        await db.rollback()
        raise


async def verify_email_verification_otp(
    db: AsyncSession,
    user: User,
    otp: str,
) -> User:
    try:
        # Lock the user row to serialize verification and OTP creation.
        user_result = await db.execute(
            select(User)
            .where(User.id == user.id)
            .with_for_update()
        )
        locked_user = user_result.scalar_one_or_none()

        if locked_user is None:
            raise ValueError("User not found")

        if locked_user.email_verified:
            raise ValueError("Email is already verified")

        result = await db.execute(
            select(EmailVerificationOTP)
            .where(
                EmailVerificationOTP.user_id == locked_user.id,
                EmailVerificationOTP.used.is_(False),
            )
            .order_by(EmailVerificationOTP.created_at.desc())
            .limit(1)
            .with_for_update()
        )
        verification_otp = result.scalar_one_or_none()

        if verification_otp is None:
            raise ValueError("No active verification OTP found")

        now = _utc_now()
        expires_at = _normalize_datetime(verification_otp.expires_at)

        if expires_at <= now:
            verification_otp.used = True
            await db.commit()
            raise ValueError("OTP has expired")

        if verification_otp.attempts >= MAX_OTP_ATTEMPTS:
            verification_otp.used = True
            await db.commit()
            raise ValueError("Maximum OTP attempts exceeded")

        is_valid = verify_otp(
            otp,
            locked_user.id,
            verification_otp.otp_hash,
            "email-verification",
        )

        if not is_valid:
            verification_otp.attempts += 1
            attempts_exceeded = (
                verification_otp.attempts >= MAX_OTP_ATTEMPTS
            )

            if attempts_exceeded:
                verification_otp.used = True

            await db.commit()

            if attempts_exceeded:
                raise ValueError("Maximum OTP attempts exceeded")

            raise ValueError("Invalid OTP")

        verification_otp.used = True
        locked_user.email_verified = True

        await db.commit()
        await db.refresh(locked_user)

        return locked_user

    except ValueError:
        if db.in_transaction():
            await db.rollback()
        raise

    except Exception:
        await db.rollback()
        raise
