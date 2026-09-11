from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth_schema import RegisterRequest
from sqlalchemy import select
from app.models.user_model import User
from app.core.security import hash_password

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