from app.services.auth_services import authenticate_user
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.auth_schema import LoginRequest
from app.database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token

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