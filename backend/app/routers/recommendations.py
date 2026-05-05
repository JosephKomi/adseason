import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.dataset import Dataset
from app.models.recommendation import Recommendation
from app.models.user import User
from app.schemas.recommendation import GenerateRequest, RecommendationListItem, RecommendationResponse
from app.services.export_service import generate_pdf
from app.services.ml_service import predict_batch
from app.services.rec_service import generate
from app.services.upload_service import load_dataframe

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.post("/generate", response_model=RecommendationResponse, status_code=201)
async def generate_recommendations(
    body: GenerateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Dataset).where(Dataset.id == body.dataset_id, Dataset.user_id == user.id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(404, "Dataset introuvable")
    if dataset.status != "processed":
        raise HTTPException(422, "Dataset invalide ou non traité correctement")

    df = load_dataframe(dataset.filename)
    df_clustered = predict_batch(df)
    clusters = generate(df_clustered, body.season, body.total_budget, body.currency)

    reco = Recommendation(
        user_id=user.id,
        dataset_id=dataset.id,
        season=body.season,
        currency=body.currency,
        total_budget=body.total_budget,
        clusters={"items": clusters},
        model_version="v1.0",
    )
    db.add(reco)
    await db.flush()

    return RecommendationResponse(
        id=reco.id,
        season=reco.season,
        currency=reco.currency,
        total_budget=float(reco.total_budget) if reco.total_budget else None,
        clusters=reco.clusters,
        model_version=reco.model_version,
        created_at=reco.created_at,
        dataset_name=dataset.original_name,
    )


@router.get("/", response_model=list[RecommendationListItem])
async def list_recommendations(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Recommendation, Dataset.original_name)
        .outerjoin(Dataset, Recommendation.dataset_id == Dataset.id)
        .where(Recommendation.user_id == user.id)
        .order_by(Recommendation.created_at.desc())
    )
    rows = result.all()
    return [
        RecommendationListItem(
            id=reco.id,
            season=reco.season,
            currency=reco.currency,
            total_budget=float(reco.total_budget) if reco.total_budget else None,
            created_at=reco.created_at,
            dataset_name=dataset_name,
        )
        for reco, dataset_name in rows
    ]


@router.get("/{reco_id}", response_model=RecommendationResponse)
async def get_recommendation(
    reco_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    reco, dataset_name = await _get_or_404(reco_id, user.id, db)
    return RecommendationResponse(
        id=reco.id,
        season=reco.season,
        currency=reco.currency,
        total_budget=float(reco.total_budget) if reco.total_budget else None,
        clusters=reco.clusters,
        model_version=reco.model_version,
        created_at=reco.created_at,
        dataset_name=dataset_name,
    )


@router.get("/{reco_id}/export/pdf")
async def export_pdf(
    reco_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    reco, _ = await _get_or_404(reco_id, user.id, db)
    pdf_bytes = generate_pdf({
        "season": reco.season,
        "total_budget": float(reco.total_budget) if reco.total_budget else 0,
        "currency": reco.currency,
        "clusters": reco.clusters.get("items", []),
    })
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=adseason-{reco.season}.pdf"},
    )


@router.delete("/{reco_id}", status_code=204)
async def delete_recommendation(
    reco_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    reco, _ = await _get_or_404(reco_id, user.id, db)
    await db.delete(reco)


async def _get_or_404(
    reco_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession
) -> tuple[Recommendation, str | None]:
    result = await db.execute(
        select(Recommendation, Dataset.original_name)
        .outerjoin(Dataset, Recommendation.dataset_id == Dataset.id)
        .where(Recommendation.id == reco_id, Recommendation.user_id == user_id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(404, "Recommandation introuvable")
    return row[0], row[1]
