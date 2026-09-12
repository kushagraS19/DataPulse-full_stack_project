from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.core.security import decode_access_token
from app.services.user_services import get_user_by_id

security = HTTPBearer()

async def get_current_user(
        credentials : HTTPAuthorizationCredentials = Depends(security),
        db : AsyncSession = Depends(get_db)
):
    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token"
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    try : 
        user_id = int(user_id)

    except (ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = await get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="user not found"
        )

    return user