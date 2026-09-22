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


def generate_email_verification_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


async def create_email_verification_otp(
    db: AsyncSession,
    user: User
):
    # Don't generate another OTP if email is already verified
    if user.email_verified:
        raise ValueError("Email is already verified")

    now = datetime.now(timezone.utc)

    # Find the latest OTP
    result = await db.execute(
        select(EmailVerificationOTP)
        .where(
            EmailVerificationOTP.user_id == user.id
        )
        .order_by(
            EmailVerificationOTP.created_at.desc()
        )
        .limit(1)
    )

    latest_otp = result.scalar_one_or_none()

    # Rate limit OTP requests
    if latest_otp:
        seconds_since_last_request = (
            now - latest_otp.created_at
        ).total_seconds()

        if seconds_since_last_request < OTP_REQUEST_COOLDOWN_SECONDS:
            remaining = int(
                OTP_REQUEST_COOLDOWN_SECONDS
                - seconds_since_last_request
            )

            raise ValueError(
                f"Please wait {remaining} seconds before requesting another OTP"
            )

    # Invalidate previous unused OTPs
    await db.execute(
        update(EmailVerificationOTP)
        .where(
            EmailVerificationOTP.user_id == user.id,
            EmailVerificationOTP.used == False
        )
        .values(used=True)
    )

    # Generate new OTP
    otp = generate_email_verification_otp()

    # Create secure digest
    otp_hash = create_otp_digest(
        otp,
        user.id,
        "email-verification"
    )

    # Create OTP record
    verification_otp = EmailVerificationOTP(
        user_id=user.id,
        otp_hash=otp_hash,
        expires_at=now + timedelta(
            minutes=OTP_EXPIRY_MINUTES
        ),
        attempts=0,
        used=False
    )

    db.add(verification_otp)

    await db.commit()
    await db.refresh(verification_otp)

    return otp


async def verify_email_verification_otp(
    db: AsyncSession,
    user: User,
    otp: str
):
    now = datetime.now(timezone.utc)

    # Find latest unused OTP
    result = await db.execute(
        select(EmailVerificationOTP)
        .where(
            EmailVerificationOTP.user_id == user.id,
            EmailVerificationOTP.used == False
        )
        .order_by(
            EmailVerificationOTP.created_at.desc()
        )
        .with_for_update()
    )

    verification_otp = result.scalars().first()

    if verification_otp is None:
        raise ValueError(
            "No active verification OTP found"
        )

    # Check expiry
    if verification_otp.expires_at <= now:
        verification_otp.used = True

        await db.commit()

        raise ValueError(
            "OTP has expired"
        )

    # Check attempt limit
    if verification_otp.attempts >= MAX_OTP_ATTEMPTS:
        verification_otp.used = True

        await db.commit()

        raise ValueError(
            "Maximum OTP attempts exceeded"
        )

    # Verify OTP
    is_valid = verify_otp(
        otp,
        user.id,
        verification_otp.otp_hash,
        "email-verification"
    )

    if not is_valid:
        verification_otp.attempts += 1

        await db.commit()

        raise ValueError(
            "Invalid OTP"
        )

    # OTP is valid
    verification_otp.used = True
    user.email_verified = True

    await db.commit()
    await db.refresh(user)

    return user