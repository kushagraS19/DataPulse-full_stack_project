from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    workspace_id: int


class ProjectUpdate(BaseModel):
    name: str


class ProjectResponse(BaseModel):
    id: int
    name: str
    workspace_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )