from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user_schema import RegisterRequest, UserUpdateRequest
from sqlalchemy import select
from app.models.user_model import User
from app.core.security import hash_password, verify_password
from fastapi import HTTPException

# CREATE USER 
async def create_user(
        db : AsyncSession,
        data : RegisterRequest
) :
    result = await db.execute(
        select(User).where(
            User.email == data.email
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        return None

    password_hash = hash_password(
        data.password
    )

    user = User(
        name = data.name,
        password_hash = password_hash,
        email = data.email
    )

    try :
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    except Exception: 
        await db.rollback()
        raise

# GET ALL USERS
async def get_all_users(db : AsyncSession):
    result = await db.execute(
        select(User)
    )

    users = result.scalars().all()

    return users

# GET USER BY ID
async def get_user_by_id(db : AsyncSession, id : int):
    result = await db.execute(
        select(User).
        where(User.id == id)
    )

    user = result.scalar_one_or_none()

    return user

# UPDATE USER
async def update_user(
        db : AsyncSession,
        user_id : int,
        data : UserUpdateRequest
):
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
                User.id != user_id
            )
        )

        existing = email_result.scalar_one_or_none()

        if existing:
            raise ValueError("Email already exist")

        user.email = data.email

    await db.commit()
    await db.refresh(user)

    return user 

# DELETE USER
async def delete_user(
        db : AsyncSession,
        user_id : int
):
    result = await db.execute(
        select(User).where(
            User.id == user_id
        )
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code = 404,
            detail = "User does not exist"
        )

    try :
        await db.delete(user)
        await db.commit()

    except Exception:
        await db.rollback()
        raise

    return user

# DELETE USER BY ADMIN
async def admin_delete_user(
        user_id : int,
        db : AsyncSession
):
    result = await db.execute(
        select(User).where(
            User.id == user_id
        )
    )

    user = result.scalars_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    try :
        await db.delete(user)
        await db.commit()

    except Exception:
        await db.rollback()
        raise

    return user

# CHANGE USER PASSWORD
async def change_password(
        db : AsyncSession,
        user : User,
        current_password : str,
        new_password : str
):
    if not verify_password(current_password,user.password_hash):
        raise ValueError("Password is incorrect")

    user.password_hash = hash_password(new_password)

    try : 
        await db.commit()
        await db.refresh(user)
    except Exception:
        await db.rollback()
        raise

async def change_user_password(
    db: AsyncSession,
    user: User,
    new_password: str
):
    user.password_hash = hash_password(new_password)

    await db.commit()
    await db.refresh(user)

    return user