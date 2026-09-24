from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_refresh_token,
    hash_refresh_token
)

from app.models.refresh_token_model import RefreshToken
from app.models.user_model import User


REFRESH_TOKEN_EXPIRE_DAYS = 7

async def create_user_refresh_token(
        db: AsyncSession,
        user : User
):
    token = create_refresh_token()

    token_hash = hash_refresh_token(
        token
    )

    refresh_token = RefreshToken(
        user_id = user.id,
        token_hash=token_hash,
        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(
                days=REFRESH_TOKEN_EXPIRE_DAYS
            )
        ),
        revoked = False
    )

    db.add(refresh_token)

    await db.commit()
    await db.refresh(refresh_token)

    return token

async def get_refresh_token(
        db : AsyncSession,
        token : str
):
    token_hash = hash_refresh_token(
        token
    )

    result = await db.execute(
        select(RefreshToken)
        .where(
            RefreshToken.token_hash == token_hash
        )
    )

    return result.scalar_one_or_none()


async def validate_refresh_token(
        db : AsyncSession,
        token : str
):
    refresh_token = await get_refresh_token(
        db,
        token
    )

    if refresh_token is None:
        raise ValueError(
            "Invalid Refresh Token"
        )

    if refresh_token.revoked:
        raise ValueError(
            "Refresh Token is revoked"
        )

    if refresh_token.expires_at <= datetime.now(
        timezone.utc
    ):
        raise ValueError(
            "Refresh Token is expired"
        )

    result = await db.execute(
        select(User)
        .where(
            User.id == RefreshToken.user_id
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise ValueError(
            "User Not Found"
        )

    return refresh_token, user  


async def revoke_refresh_token(
        db : AsyncSession,
        token : str
):
    refresh_token = await get_refresh_token(
        db,
        token
    )

    if refresh_token is None:
        raise ValueError(
            "Invalid refresh token"
        )

    refresh_token.revoked = True

    await db.commit()