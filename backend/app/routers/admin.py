from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_admin
from app.models.model_version import ModelVersion
from app.models.user import User
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


@router.get("/model/versions")
async def list_model_versions(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ModelVersion).order_by(ModelVersion.trained_at.desc()))
    return result.scalars().all()


@router.post("/model/retrain")
async def retrain(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.services.ml_service import train
    from app.services.upload_service import load_dataframe
    import pandas as pd
    from pathlib import Path

    data_path = Path("../data/DATASET_CLUSTERISE.csv")
    if not data_path.exists():
        return {"error": "Dataset source introuvable"}

    df = pd.read_csv(data_path, sep=";", encoding="latin1")
    result = train(df)

    mv = ModelVersion(version="v1.0", **result, is_active=True)
    db.add(mv)
    await db.flush()
    return result
