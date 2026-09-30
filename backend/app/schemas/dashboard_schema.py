from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DashboardCreate(BaseModel):
    name: str
    project_id: int
    workspace_id: int


class DashboardResponse(BaseModel):
    id: int
    name: str
    project_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )