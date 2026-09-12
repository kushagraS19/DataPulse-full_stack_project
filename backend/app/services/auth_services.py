from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.models.user_model import User

async def authenticate_user(
        db : AsyncSession,
        email : str,
        password : str
):
    result = await db.execute(
        select(User).where(
            User.email == email
        )
    )

    user = result.scalar_one_or_none()

    if not user:
        return None

    valid_password = verify_password(
        password,
        user.password_hash
    )

    if not valid_password:
        return None

    return user