import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class GenerateRequest(BaseModel):
    dataset_id: uuid.UUID
    season: str
    currency: str = "EUR"
    total_budget: float
    channels: list[str] = []


class ClusterReco(BaseModel):
    cluster_id: int
    client_type: str
    description: str
    product_category: str
    offer_type: str
    channels: list[str]
    budget: float
    currency: str
    roi_estimate: float
    target_size: int
    target_pct: float


class RecommendationResponse(BaseModel):
    id: uuid.UUID
    season: str
    currency: str
    total_budget: float | None
    clusters: dict
    model_version: str | None
    created_at: datetime
    dataset_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RecommendationListItem(BaseModel):
    id: uuid.UUID
    season: str
    currency: str
    total_budget: float | None
    created_at: datetime
    dataset_name: str | None = None

    model_config = ConfigDict(from_attributes=True)
