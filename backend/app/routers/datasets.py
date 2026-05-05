import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.dataset import Dataset
from app.models.user import User
from app.schemas.dataset import DatasetPreview, DatasetResponse
from app.services.upload_service import load_dataframe, save_and_parse

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.post("/upload", response_model=DatasetResponse, status_code=201)
async def upload(
    file: UploadFile,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    parsed = await save_and_parse(file)
    dataset = Dataset(
        user_id=user.id,
        original_name=file.filename,
        **{k: parsed[k] for k in ("filename", "file_size", "row_count", "columns", "status", "error_msg")},
    )
    db.add(dataset)
    await db.flush()
    return dataset


@router.get("/", response_model=list[DatasetResponse])
async def list_datasets(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Dataset).where(Dataset.user_id == user.id).order_by(Dataset.upload_date.desc())
    )
    return result.scalars().all()


@router.get("/{dataset_id}/preview", response_model=DatasetPreview)
async def preview(
    dataset_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    dataset = await _get_or_404(dataset_id, user.id, db)
    df = load_dataframe(dataset.filename)

    return {
        "columns": list(df.columns),
        "sample_rows": df.head(10).fillna("").to_dict("records"),
        "stats": df.describe().fillna("").to_dict(),
        "missing_required": dataset.error_msg.replace("Colonnes manquantes : ", "").strip("[]").split(", ")
        if dataset.error_msg else [],
    }


@router.delete("/{dataset_id}", status_code=204)
async def delete_dataset(
    dataset_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    dataset = await _get_or_404(dataset_id, user.id, db)
    filepath = Path(settings.UPLOAD_DIR) / dataset.filename
    if filepath.exists():
        filepath.unlink()
    await db.delete(dataset)


async def _get_or_404(dataset_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> Dataset:
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id, Dataset.user_id == user_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(404, "Dataset introuvable")
    return dataset
