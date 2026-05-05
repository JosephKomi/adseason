from datetime import datetime
from pydantic import BaseModel


class GenerateRequest(BaseModel):
    dataset_id: str
    season: str  # printemps | ete | automne | hiver
    currency: str = "EUR"
    total_budget: float
    channels: list[str] = []


class ClusterReco(BaseModel):
    cluster_id: int
    client_type: str
    product_category: str
    offer_type: str
    channels: list[str]
    budget: float
    roi_estimate: float
    target_size: int
    description: str


class RecommendationResponse(BaseModel):
    id: str
    season: str
    currency: str
    total_budget: float | None
    clusters: dict
    model_version: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class RecommendationListItem(BaseModel):
    id: str
    season: str
    currency: str
    total_budget: float | None
    created_at: datetime
    dataset_name: str | None

    class Config:
        from_attributes = True
