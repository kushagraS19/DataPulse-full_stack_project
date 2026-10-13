
from datetime import datetime, timedelta, timezone
import secrets

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_refresh_token,
    hash_refresh_token,
)
from app.models.refresh_token_model import RefreshToken
from app.models.user_model import User


REFRESH_TOKEN_EXPIRE_DAYS = 7


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


async def create_user_refresh_token(
    db: AsyncSession,
    user: User,
) -> str:
    token = create_refresh_token()

    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(token),
        token_family=secrets.token_hex(32),
        token_version=user.token_version,
        expires_at=_utc_now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False,
    )

    try:
        db.add(refresh_token)
        await db.commit()
        await db.refresh(refresh_token)
    except Exception:
        await db.rollback()
        raise

    return token


async def get_refresh_token(
    db: AsyncSession,
    token: str,
):
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(token)
        )
    )
    return result.scalar_one_or_none()


async def revoke_token_family(
    db: AsyncSession,
    token_family: str,
) -> None:
    try:
        await db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.token_family == token_family,
                RefreshToken.revoked.is_(False),
            )
            .values(revoked=True)
        )
        await db.commit()
    except Exception:
        await db.rollback()
        raise


async def validate_refresh_token(
    db: AsyncSession,
    token: str,
):
    refresh_token = await get_refresh_token(db, token)

    if refresh_token is None:
        raise ValueError("Invalid refresh token")

    if refresh_token.revoked:
        await revoke_token_family(db, refresh_token.token_family)
        raise ValueError(
            "Refresh token reuse detected. Session has been revoked."
        )

    if _normalize_datetime(refresh_token.expires_at) <= _utc_now():
        raise ValueError("Refresh token has expired")

    result = await db.execute(
        select(User).where(User.id == refresh_token.user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise ValueError("User not found")

    if not user.is_active:
        raise ValueError("User account is inactive")

    if refresh_token.token_version != user.token_version:
        raise ValueError("Refresh token has been invalidated")

    return refresh_token, user


async def revoke_refresh_token(
    db: AsyncSession,
    token: str,
) -> None:
    try:
        result = await db.execute(
            select(RefreshToken)
            .where(RefreshToken.token_hash == hash_refresh_token(token))
            .with_for_update()
        )
        refresh_token = result.scalar_one_or_none()

        if refresh_token is None:
            raise ValueError("Invalid refresh token")

        if refresh_token.revoked:
            await db.execute(
                update(RefreshToken)
                .where(
                    RefreshToken.token_family == refresh_token.token_family,
                    RefreshToken.revoked.is_(False),
                )
                .values(revoked=True)
            )
            await db.commit()
            raise ValueError(
                "Refresh token reuse detected. Session has been revoked."
            )

        if _normalize_datetime(refresh_token.expires_at) <= _utc_now():
            raise ValueError("Refresh token has expired")

        refresh_token.revoked = True
        await db.commit()

    except ValueError:
        if db.in_transaction():
            await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise


async def rotate_refresh_token(
    db: AsyncSession,
    token: str,
):
    try:
        result = await db.execute(
            select(RefreshToken)
            .where(
                RefreshToken.token_hash == hash_refresh_token(token)
            )
            .with_for_update()
        )
        refresh_token = result.scalar_one_or_none()

        if refresh_token is None:
            raise ValueError("Invalid refresh token")

        if refresh_token.revoked:
            # Revoke all remaining tokens in this family.
            await db.execute(
                update(RefreshToken)
                .where(
                    RefreshToken.token_family == refresh_token.token_family,
                    RefreshToken.revoked.is_(False),
                )
                .values(revoked=True)
            )
            await db.commit()
            raise ValueError(
                "Refresh token reuse detected. Session has been revoked."
            )

        if _normalize_datetime(refresh_token.expires_at) <= _utc_now():
            raise ValueError("Refresh token has expired")

        result = await db.execute(
            select(User)
            .where(User.id == refresh_token.user_id)
            .with_for_update()
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise ValueError("User not found")

        if not user.is_active:
            raise ValueError("User account is inactive")

        if refresh_token.token_version != user.token_version:
            raise ValueError("Refresh token has been invalidated")

        # Revoke the old token and create its replacement atomically.
        refresh_token.revoked = True

        new_token = create_refresh_token()

        db.add(
            RefreshToken(
                user_id=user.id,
                token_hash=hash_refresh_token(new_token),
                token_family=refresh_token.token_family,
                token_version=user.token_version,
                expires_at=_utc_now()
                + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
                revoked=False,
            )
        )

        await db.commit()
        return new_token, user

    except ValueError:
        # Do not undo a reuse-detection revocation that was committed.
        if db.in_transaction():
            await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise
