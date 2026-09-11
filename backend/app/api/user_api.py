from fastapi import APIRouter, Depends , HTTPException
from app.schemas.auth_schema import UserResponse, RegisterRequest
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.services.user_services import create_user, get_all_users

router = APIRouter(
    prefix = "/users",
    tags = ["Users"]
)

@router.post(
    "/register",
    response_model = UserResponse
)
async def register(
    data : RegisterRequest,
    db : AsyncSession = Depends(get_db)
) : 
    user = await create_user(db , data)

    if user is None:
        raise HTTPException(
            status_code=400,
            detail = "Email Already Exist"
        )

    return user

@router.get(
    "/get-users",
    response_model = list[UserResponse]
)
async def get_all_users_api(
    db : AsyncSession = Depends(get_db)
):
    return await get_all_users(db)