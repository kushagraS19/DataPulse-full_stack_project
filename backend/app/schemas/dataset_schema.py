from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DatasetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    file_path: str = Field(min_length=1, max_length=1024)
    project_id: int = Field(gt=0)
    workspace_id: int = Field(gt=0)

    model_config = ConfigDict(str_strip_whitespace=True)


class DatasetUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=150)

    model_config = ConfigDict(str_strip_whitespace=True)


class DatasetResponse(BaseModel):
    id: int
    name: str
    file_path: str
    project_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetPreviewResponse(BaseModel):
    dataset_id: int
    columns: list[str]
    row_count: int
    preview: list[dict[str, Any]]