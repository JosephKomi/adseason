import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, JSON, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=False), primary_key=True, default=uuid.uuid4)
    version: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    n_clusters: Mapped[int | None] = mapped_column(Integer)
    features: Mapped[list | None] = mapped_column(JSON)
    silhouette_score: Mapped[float | None] = mapped_column(Numeric(5, 4))
    training_rows: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    trained_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
