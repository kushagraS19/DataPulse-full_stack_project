from app.services.auth_services import authenticate_user
from sqlalchemy import select
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.auth_schema import LoginRequest, PasswordResetRequest, PasswordResetVerifyRequest
from app.database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token
from app.models.user_model import User
from app.services.password_reset_otp_services import (
    create_password_reset_otp,
    verify_password_reset_otp,
)
from app.services.email_services import (
    send_password_change_otp,
)
from app.services.user_services import (
    change_user_password,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login")
async def login(
    data : LoginRequest,
    db : AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, data.email, data.password)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        {
            "sub" : str(user.id),
            "token_version" : user.token_version
        }
    )

    return {
        "access_token" : access_token,
        "token_type" : "bearer"
    }

@router.post("/password-reset/request")
async def request_password_reset(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(
            User.email == data.email
        )
    )

    user = result.scalar_one_or_none()

    # Don't reveal whether the email exists
    if user is None:
        return {
            "message": (
                "If an account exists for this email, "
                "an OTP has been sent."
            )
        }

    try:
        otp = await create_password_reset_otp(
            db,
            user
        )

        await send_password_change_otp(
            user.email,
            otp
        )

    except ValueError as e:
        raise HTTPException(
            status_code=429,
            detail=str(e)
        )

    return {
        "message": (
            "If an account exists for this email, "
            "an OTP has been sent."
        )
    }

@router.post("/password-reset/verify")
async def verify_password_reset(
    data: PasswordResetVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(
            User.email == data.email
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP or reset request"
        )

    try:
        await verify_password_reset_otp(
            db,
            user,
            data.otp
        )

        await change_user_password(
            db,
            user,
            data.new_password
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {
        "message": "Password reset successfully"
    }