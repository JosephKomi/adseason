import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(native_uuid=False), ForeignKey("datasets.id"))
    season: Mapped[str] = mapped_column(String, nullable=False)
    currency: Mapped[str] = mapped_column(String, default="EUR")
    total_budget: Mapped[float | None] = mapped_column(Numeric(12, 2))
    clusters: Mapped[dict] = mapped_column(JSON, nullable=False)
    model_version: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="recommendations")
    dataset: Mapped["Dataset"] = relationship(back_populates="recommendations")
