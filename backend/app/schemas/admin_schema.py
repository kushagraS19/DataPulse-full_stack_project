from datetime import datetime

from pydantic import BaseModel, EmailStr


class AdminOverviewResponse(BaseModel):
    total_users: int
    verified_users: int
    unverified_users: int
    total_workspaces: int
    total_projects: int
    total_datasets: int
    total_dashboards: int
    total_charts: int
    total_rows: int
    storage_bytes: int


class AdminUserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    email_verified: bool
    created_at: datetime
    workspace_count: int
    project_count: int
    dataset_count: int
    dashboard_count: int
    chart_count: int
    is_active : bool


class AdminUserListResponse(BaseModel):
    items: list[AdminUserResponse]
    total: int
    limit: int
    offset: int