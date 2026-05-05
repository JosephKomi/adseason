import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DatasetResponse(BaseModel):
    id: uuid.UUID
    original_name: str
    file_size: int | None
    row_count: int | None
    columns: dict | None
    status: str
    error_msg: str | None
    upload_date: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetPreview(BaseModel):
    columns: list[str]
    sample_rows: list[dict]
    stats: dict
    missing_required: list[str]
