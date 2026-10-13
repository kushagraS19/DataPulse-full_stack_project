
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.models.user_model import User


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    # Do not reveal whether an email exists.
    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    if not user.email_verified:
        raise ValueError("Please verify your email before logging in")

    if not user.is_active:
        raise ValueError("User account is inactive")

    return user
