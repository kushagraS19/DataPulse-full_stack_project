from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DatasetCreate(BaseModel):
    name: str
    file_path: str
    project_id: int
    workspace_id : int


class DatasetResponse(BaseModel):
    id: int
    name: str
    file_path: str
    project_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class DatasetPreviewResponse(BaseModel):
    dataset_id: int
    columns: list[str]
    row_count: int
    preview: list[dict]