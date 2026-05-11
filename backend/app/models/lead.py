from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    ranking_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ranking_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_ranked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    assigned_to: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    routing_reason: Mapped[str | None] = mapped_column(String(256), nullable=True)
    last_routed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )


def serialize_lead(lead: Lead) -> dict[str, Any]:
    return {
        "id": str(lead.id),
        "email": lead.email,
        "source": lead.source,
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
        "ranking_score": lead.ranking_score,
        "ranking_explanation": lead.ranking_explanation,
        "last_ranked_at": (lead.last_ranked_at.isoformat() if lead.last_ranked_at else None),
        "assigned_to": lead.assigned_to,
        "routing_reason": lead.routing_reason,
        "last_routed_at": (lead.last_routed_at.isoformat() if lead.last_routed_at else None),
    }
