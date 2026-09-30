from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChartCreate(BaseModel):
    name: str
    chart_type: str
    dashboard_id: int
    dataset_id : int
    project_id: int
    workspace_id: int
    group_by: str | None = None
    operation: str | None = None
    column: str | None = None


class ChartResponse(BaseModel):
    id: int
    name: str
    chart_type: str
    dashboard_id: int
    dataset_id : int
    group_by: str | None
    operation: str | None
    column: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )