
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user_schema import RegisterRequest, UserUpdateRequest
from app.models.user_model import User
from app.core.security import hash_password, verify_password


# CREATE USER
async def create_user(
    db: AsyncSession,
    data: RegisterRequest,
):
    try:
        result = await db.execute(
            select(User).where(User.email == data.email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            return None

        user = User(
            name=data.name,
            password_hash=hash_password(data.password),
            email=data.email,
            role="user",
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    except Exception:
        await db.rollback()
        raise


# GET ALL USERS
async def get_all_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()


# GET USER BY ID
async def get_user_by_id(db: AsyncSession, id: int):
    result = await db.execute(
        select(User).where(User.id == id)
    )
    return result.scalar_one_or_none()


# UPDATE USER
async def update_user(
    db: AsyncSession,
    user_id: int,
    data: UserUpdateRequest,
):
    try:
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return None

        if "name" in data.model_fields_set:
            user.name = data.name

        if "email" in data.model_fields_set:
            email_result = await db.execute(
                select(User).where(
                    User.email == data.email,
                    User.id != user_id,
                )
            )

            if email_result.scalar_one_or_none():
                raise ValueError("Email already exists")

            user.email = data.email

        await db.commit()
        await db.refresh(user)
        return user

    except Exception:
        await db.rollback()
        raise


# DELETE USER
async def delete_user(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User does not exist",
        )

    try:
        await db.delete(user)
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return user


# DELETE USER BY ADMIN
async def admin_delete_user(
    user_id: int,
    db: AsyncSession,
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    try:
        await db.delete(user)
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return user


# CHANGE PASSWORD
async def change_password(
    db: AsyncSession,
    user: User,
    current_password: str,
    new_password: str,
):
    if not verify_password(current_password, user.password_hash):
        raise ValueError("Password is incorrect")

    try:
        user.password_hash = hash_password(new_password)
        user.token_version = (user.token_version or 0) + 1

        await db.commit()
        await db.refresh(user)
        return user

    except Exception:
        await db.rollback()
        raise


# CHANGE PASSWORD AFTER OTP VERIFICATION
async def change_user_password(
    db: AsyncSession,
    user: User,
    new_password: str,
):
    try:
        user.password_hash = hash_password(new_password)
        user.token_version = (user.token_version or 0) + 1

        await db.commit()
        await db.refresh(user)
        return user

    except Exception:
        await db.rollback()
        raise
