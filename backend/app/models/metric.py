from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


METRIC_LEAD_CREATED = "lead_created"
METRIC_LEAD_ENRICHED = "lead_enriched"
METRIC_LEAD_RANKED = "lead_ranked"
METRIC_LEAD_ROUTED = "lead_routed"
METRIC_TASK_COMPLETED = "task_completed"
METRIC_TASK_FAILED = "task_failed"
METRIC_AI_SUMMARY_GENERATED = "ai_summary_generated"
METRIC_AI_INSIGHT_GENERATED = "ai_insight_generated"
METRIC_AI_EMBEDDING_GENERATED = "ai_embedding_generated"
METRIC_VERTICAL_INGESTION_COUNT = "vertical_ingestion_count"


KNOWN_METRIC_TYPES: frozenset[str] = frozenset(
    {
        METRIC_LEAD_CREATED,
        METRIC_LEAD_ENRICHED,
        METRIC_LEAD_RANKED,
        METRIC_LEAD_ROUTED,
        METRIC_TASK_COMPLETED,
        METRIC_TASK_FAILED,
        METRIC_AI_SUMMARY_GENERATED,
        METRIC_AI_INSIGHT_GENERATED,
        METRIC_AI_EMBEDDING_GENERATED,
        METRIC_VERTICAL_INGESTION_COUNT,
    }
)


class Metric(Base):
    __tablename__ = "metric"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    metric_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    labels: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )


def serialize_metric(metric: Metric) -> dict[str, Any]:
    return {
        "id": str(metric.id),
        "metric_type": metric.metric_type,
        "value": float(metric.value) if metric.value is not None else 0.0,
        "labels": metric.labels,
        "created_at": metric.created_at.isoformat() if metric.created_at else None,
    }
