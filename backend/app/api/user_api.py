from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.database import get_db
from app.models.user_model import User
from app.core.dependencies import get_current_user, get_admin

from app.schemas.auth_schema import(
    UserResponse,
    PasswordChangeVerifyRequest,
)
from app.schemas.user_schema import(
    RegisterRequest,
    UserUpdateRequest,
    ChangePasswordRequest,
)
from app.schemas.admin_schema import(
    AdminOverviewResponse,
    AdminUserListResponse,
)

from app.services.user_services import(
    create_user,
    get_all_users,
    get_user_by_id,
    update_user,
    delete_user,
    admin_delete_user,
    change_password,
    change_user_password,
)
from app.services.audit_log_services import get_audit_logs
from app.services.admin_services import(
    get_admin_overview,
    get_admin_users,
)
from app.services.password_otp_services import(
    create_password_change_otp,
    verify_password_change_otp,
)
from app.services.email_verification_otp_services import(
    create_email_verification_otp,
)
from app.services.email_services import(
    send_password_change_otp,
    send_email_verification_otp,
)

from app.services.audit_log_services import create_audit_log

from app.schemas.admin_control_schema import(
    AdminRoleUpdateRequest,
    AdminAccountStatusRequest,
)
from app.services.admin_services import(
    update_user_role,
    set_user_active_status,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# REGISTER USER
@router.post("/register", response_model=UserResponse)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await create_user(db, data)

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Email Already Exist",
        )

    try:
        otp = await create_email_verification_otp(db, user)
        await send_email_verification_otp(user.email, otp)

    except ValueError as e:
        raise HTTPException(
            status_code=429,
            detail=str(e),
        )

    return user


# CURRENT USER PROFILE
@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


# ADMIN OVERVIEW
@router.get(
    "/admin/overview",
    response_model=AdminOverviewResponse,
)
async def admin_overview(
    current_user: User = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    return await get_admin_overview(db)


# ADMIN USER LIST WITH SEARCH AND PAGINATION
@router.get(
    "/admin/users",
    response_model=AdminUserListResponse,
)
async def admin_users(
    search: str | None = Query(default=None, max_length=100),
    role: str | None = Query(default=None, pattern="^(user|admin)$"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    return await get_admin_users(
        db=db,
        limit=limit,
        offset=offset,
        search=search,
        role=role,
    )


# EXISTING ADMIN ROUTE - KEPT FOR COMPATIBILITY
@router.get(
    "/get-users",
    response_model=list[UserResponse],
)
async def get_all_users_api(
    current_user: User = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    return await get_all_users(db)


# ADMIN: CHANGE USER ROLE
@router.patch("/admin/users/{user_id}/role")
async def admin_update_user_role(
    user_id: int,
    data: AdminRoleUpdateRequest,
    current_user: User = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await update_user_role(
            db=db,
            user_id=user_id,
            new_role=data.role,
            admin_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "User role updated successfully",
        "user_id": user.id,
        "role": user.role,
    }


# ADMIN: ACTIVATE OR DEACTIVATE USER
@router.patch("/admin/users/{user_id}/status")
async def admin_update_user_status(
    user_id: int,
    data: AdminAccountStatusRequest,
    current_user: User = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await set_user_active_status(
            db=db,
            user_id=user_id,
            is_active=data.is_active,
            admin_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    await create_audit_log(
        db=db,
        admin_id=current_user.id,
        action="user_activated" if data.is_active else "user_deactivated",
        target_user_id=user_id,
        details={"is_active": data.is_active},
    )

    return {
        "message": (
            "User account activated successfully"
            if user.is_active
            else "User account deactivated successfully"
        ),
        "user_id": user.id,
        "is_active": user.is_active,
    }


# GIVE USER BY ID
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User Not Found",
        )

    return user


# UPDATE CURRENT USER PROFILE
@router.patch("/update/me", response_model=UserResponse)
async def update_my_profile(
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await update_user(db, current_user.id, data)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


# DELETE CURRENT USER
@router.delete("/delete/me")
async def user_delete(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role == "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin accounts cannot be deleted through this endpoint",
        )

    await delete_user(db, current_user.id)

    return {"message": "Account deleted successfully"}


# ADMIN DELETE USER
@router.delete("/admin-delete/{user_id}")
async def admin_delete_user_api(
    user_id: int,
    current_user: User = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete your own admin account",
        )

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    target_user = result.scalar_one_or_none()

    if target_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if target_user.role == "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin accounts cannot be deleted through this endpoint",
        )

    deleted_user_email = target_user.email
    deleted_user_name = target_user.name

    await admin_delete_user(user_id, db)

    await create_audit_log(
        db=db,
        admin_id=current_user.id,
        action="user_deleted",
        target_user_id=user_id,
        details={
            "deleted_user_id": user_id,
            "deleted_user_email": deleted_user_email,
            "deleted_user_name": deleted_user_name,
        },
    )

    return {"message": "User deleted successfully"}


# ADMIN AUDIT LOGS
@router.get("/admin/audit-logs")
async def get_admin_audit_logs_api(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100",
        )

    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="Offset cannot be negative",
        )

    logs = await get_audit_logs(
        db=db,
        limit=limit,
        offset=offset,
    )

    return [
        {
            "id": log.id,
            "admin_id": log.admin_id,
            "action": log.action,
            "target_user_id": log.target_user_id,
            "details": log.details,
            "created_at": log.created_at,
        }
        for log in logs
    ]


# CHANGE PASSWORD
@router.patch("/change-password")
async def change_user_password_api(
    data: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await change_password(
            db,
            user,
            data.current_password,
            data.new_password,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return {"message": "Password changed successfully"}


# REQUEST PASSWORD CHANGE OTP
@router.post("/password-change/request")
async def request_password_change_otp(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        otp = await create_password_change_otp(db, current_user)
        await send_password_change_otp(current_user.email, otp)

    except ValueError as e:
        raise HTTPException(
            status_code=429,
            detail=str(e),
        )

    return {"message": "OTP sent successfully"}


# VERIFY PASSWORD CHANGE OTP
@router.post("/password-change/verify")
async def verify_password_change(
    data: PasswordChangeVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await verify_password_change_otp(
            db,
            current_user,
            data.otp,
        )

        await change_user_password(
            db,
            current_user,
            data.new_password,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return {"message": "Password changed successfully"}