import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.dataset import Dataset
from app.models.user import User
from app.services.ml_service import predict_batch
from app.services.upload_service import load_dataframe

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

SEASON_MAP = {
    1: "Hiver", 2: "Hiver", 3: "Printemps", 4: "Printemps", 5: "Printemps",
    6: "Eté", 7: "Eté", 8: "Eté", 9: "Automne", 10: "Automne",
    11: "Automne", 12: "Hiver",
}


@router.get("/kpis/{dataset_id}")
async def get_kpis(
    dataset_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    df = await _load_df(dataset_id, user.id, db)
    return {
        "total_orders": len(df),
        "total_customers": (
            int(df["customer_unique_id"].nunique())
            if "customer_unique_id" in df.columns
            else len(df)
        ),
        "avg_basket": (
            round(float(df["payment_value"].mean()), 2)
            if "payment_value" in df.columns
            else 0.0
        ),
        "avg_review_score": (
            round(float(df["review_score"].mean()), 2)
            if "review_score" in df.columns
            else 0.0
        ),
        "total_revenue": (
            round(float(df["payment_value"].sum()), 2)
            if "payment_value" in df.columns
            else 0.0
        ),
    }


@router.get("/seasonal/{dataset_id}")
async def get_seasonal(
    dataset_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    df = await _load_df(dataset_id, user.id, db)
    if "month" not in df.columns:
        raise HTTPException(422, "Colonne 'month' manquante dans le dataset")

    df = df.copy()
    df["season"] = df["month"].map(SEASON_MAP)

    agg: dict = {"orders": ("month", "count")}
    if "payment_value" in df.columns:
        agg["avg_basket"] = ("payment_value", "mean")

    result = df.groupby("season").agg(**agg).reset_index()
    result = result.round(2)
    return result.to_dict("records")


@router.get("/categories/{dataset_id}")
async def get_categories(
    dataset_id: uuid.UUID,
    top: int = 10,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    df = await _load_df(dataset_id, user.id, db)
    col = next(
        (c for c in df.columns if "categor" in c.lower() or "product_category" in c.lower()),
        None,
    )
    if not col:
        raise HTTPException(422, "Colonne de catégories introuvable dans le dataset")

    counts = df[col].value_counts().head(top).reset_index()
    counts.columns = ["category", "count"]
    return counts.to_dict("records")


@router.get("/clusters/{dataset_id}")
async def get_clusters(
    dataset_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    df = await _load_df(dataset_id, user.id, db)
    df_c = predict_batch(df)
    dist = df_c["cluster"].value_counts().reset_index()
    dist.columns = ["cluster", "count"]
    return dist.to_dict("records")


@router.get("/trends/{dataset_id}")
async def get_trends(
    dataset_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    df = await _load_df(dataset_id, user.id, db)
    if "month" not in df.columns:
        raise HTTPException(422, "Colonne 'month' manquante dans le dataset")

    df = df.copy()
    agg: dict = {"orders": ("month", "count")}
    if "payment_value" in df.columns:
        agg["revenue"] = ("payment_value", "sum")

    result = df.groupby("month").agg(**agg).reset_index()
    result = result.sort_values("month").round(2)
    return result.to_dict("records")


@router.post("/predict")
async def predict_single(
    data: dict,
    user: User = Depends(get_current_user),
):
    from app.services.ml_service import predict_cluster
    cluster = predict_cluster(data)
    return {"cluster": cluster}


async def _load_df(dataset_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession):
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id, Dataset.user_id == user_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(404, "Dataset introuvable")
    if dataset.status != "processed":
        raise HTTPException(422, "Dataset non traité")
    return load_dataframe(dataset.filename)
