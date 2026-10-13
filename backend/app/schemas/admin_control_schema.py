from pydantic import BaseModel, Field


class AdminRoleUpdateRequest(BaseModel):
    role: str = Field(pattern="^(user|admin)$")


class AdminAccountStatusRequest(BaseModel):
    is_active: bool