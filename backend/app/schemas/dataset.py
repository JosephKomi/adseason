from datetime import datetime
from pydantic import BaseModel


class DatasetResponse(BaseModel):
    id: str
    original_name: str
    file_size: int | None
    row_count: int | None
    columns: dict | None
    status: str
    error_msg: str | None
    upload_date: datetime

    class Config:
        from_attributes = True


class DatasetPreview(BaseModel):
    columns: list[str]
    sample_rows: list[dict]
    stats: dict
    missing_required: list[str]
