from fastapi import APIRouter, Depends , HTTPException,Body
from app.schemas.auth_schema import UserResponse
from app.schemas.user_schema import RegisterRequest, UserUpdateRequest
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.services.user_services import create_user, get_all_users, get_user_by_id, update_user, delete_user, admin_delete_user
from app.models.user_model import User
from app.core.dependencies import get_current_user, get_admin

router = APIRouter(
    prefix = "/users",
    tags = ["Users"]
)

# REGISTER USER
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

# ME 
@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user : User = Depends(get_current_user)
):
    return current_user

# GIVES ALL USER
@router.get(
    "/get-users",
    response_model = list[UserResponse]
)
async def get_all_users_api(

    current_user : User = Depends(get_admin),
    db : AsyncSession = Depends(get_db)
):
    return await get_all_users(db)

# GIVE USER BY ID
@router.get(
    "/{user_id}",
    response_model = UserResponse
)
async def get_user(
    user_id : int,
    current_user : User = Depends(get_admin),
    db : AsyncSession = Depends(get_db),
) :
    user = await get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code = 404,
            detail = "User Not Found"
        )

    return user

@router.patch(
    "/update/me",
    response_model = UserResponse
)
async def update_my_profile(
    data : UserUpdateRequest,
    current_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db)
):
    try:
        user = await update_user(db, current_user.id, data)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if user is None:
        raise HTTPException(
            status_code = 404,
            detail = "User not found"
        )

    return user

# User delete
@router.delete(
    "/delete/me"
)
async def user_delete(
    current_user : User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db)
):
    user = await delete_user(db, current_user.id)

    return user

# Admin delete user
@router.delete("/admin-delete/{user_id}", response_model=UserResponse)
async def admin_delete_user_api(
    user_id : int,
    current_user : User = Depends(get_admin),
    db : AsyncSession = Depends(get_db)
):
    user = await admin_delete_user(user_id,db)

    return user