
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth_schema import (
    LoginRequest,
    PasswordResetRequest,
    PasswordResetVerifyRequest,
    EmailVerificationVerifyRequest,
    EmailVerificationRequest,
)
from app.database.database import get_db
from app.core.dependencies import (
    get_current_user,
    validate_request_origin,
)
from app.core.security import create_access_token
from app.core.config import settings
from app.models.user_model import User

from app.services.auth_services import authenticate_user
from app.services.password_reset_otp_services import (
    create_password_reset_otp,
    verify_password_reset_otp,
)
from app.services.email_services import (
    send_password_change_otp,
    send_email_verification_otp,
)
from app.services.user_services import change_user_password
from app.services.email_verification_otp_services import (
    create_email_verification_otp,
    verify_email_verification_otp,
)
from app.services.refresh_token_service import (
    create_user_refresh_token,
    revoke_refresh_token,
    rotate_refresh_token,
)
from app.services.login_attempt_services import (
    get_login_attempt,
    is_login_locked,
    record_failed_login,
    reset_login_attempts,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login")
async def login(
    data: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(validate_request_origin),
):
    ip_address = request.client.host if request.client else "unknown"

    attempts = await get_login_attempt(
        db,
        data.email,
        ip_address,
    )

    locked = await is_login_locked(
        db,
        data.email,
        ip_address,
    )

    if locked and attempts and attempts.locked_until:
        locked_until = attempts.locked_until

        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=timezone.utc)

        remaining_seconds = (
            locked_until - datetime.now(timezone.utc)
        ).total_seconds()

        remaining_minutes = max(
            1,
            int(remaining_seconds / 60) + 1,
        )

        raise HTTPException(
            status_code=429,
            detail=(
                "Too many failed login attempts. "
                f"Please try again after {remaining_minutes} minutes."
            ),
        )

    try:
        user = await authenticate_user(
            db,
            data.email,
            data.password,
        )
    except ValueError:
        await record_failed_login(
            db,
            data.email,
            ip_address,
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        ) from None

    if user is None:
        await record_failed_login(
            db,
            data.email,
            ip_address,
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    await reset_login_attempts(
        db,
        data.email,
        ip_address,
    )

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "token_version": user.token_version,
        }
    )

    refresh_token = await create_user_refresh_token(db, user)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT.lower() == "production",
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/password-reset/request")
async def request_password_reset(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    generic_response = {
        "message": (
            "If an account exists for this email, "
            "an OTP has been sent."
        )
    }

    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    user = result.scalar_one_or_none()

    if user is None:
        return generic_response

    try:
        otp = await create_password_reset_otp(db, user)

        await send_password_change_otp(user.email, otp)
    except ValueError:
        return generic_response

    return generic_response


@router.post("/password-reset/verify")
async def verify_password_reset(
    data: PasswordResetVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP or reset request",
        )

    try:
        await verify_password_reset_otp(db, user, data.otp)
        await change_user_password(db, user, data.new_password)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from None

    return {"message": "Password reset successfully"}


@router.post("/email-verification/request")
async def request_email_verification(
    data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    generic_response = {
        "message": (
            "If an account exists for this email, "
            "a verification email has been sent."
        )
    }

    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    user = result.scalar_one_or_none()

    if user is None or user.email_verified:
        return generic_response

    try:
        otp = await create_email_verification_otp(db, user)
        await send_email_verification_otp(user.email, otp)
    except ValueError:
        return generic_response

    return generic_response


@router.post("/email-verification/verify")
async def verify_email_verification(
    data: EmailVerificationVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid email or OTP",
        )

    if user.email_verified:
        return {"message": "Email is already verified"}

    try:
        await verify_email_verification_otp(db, user, data.otp)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from None

    return {"message": "Email verified successfully"}


@router.post("/refresh")
async def refresh_access_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(validate_request_origin),
):
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token is None:
        raise HTTPException(
            status_code=401,
            detail="Refresh token not found",
        )

    try:
        refresh_token, user = await rotate_refresh_token(
            db,
            refresh_token,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        ) from None

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "token_version": user.token_version,
        }
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT.lower() == "production",
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(validate_request_origin),
):
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token is not None:
        try:
            await revoke_refresh_token(db, refresh_token)
        except ValueError as e:
            raise HTTPException(
                status_code=401,
                detail=str(e),
            ) from None

    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=settings.ENVIRONMENT.lower() == "production",
        samesite="lax",
        path="/",
    )

    return {"message": "Logged out successfully"}
