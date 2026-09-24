from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.models.user_model import User

async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str
):
    result = await db.execute(
        select(User).where(User.email == email)
    )

    user = result.scalar_one_or_none()

    if user is None:
        return None

    if not verify_password(
        password,
        user.password_hash
    ):
        return None

    if not user.email_verified:
        raise ValueError(
            "Please verify your email before logging in"
        )

    return user