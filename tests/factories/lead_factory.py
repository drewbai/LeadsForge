"""Factory helpers for Lead model instances."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from app.models.lead import Lead
from sqlalchemy.ext.asyncio import AsyncSession

_COUNTER = {"n": 0}


def _next_email() -> str:
    _COUNTER["n"] += 1
    return f"lead{_COUNTER['n']}-{uuid4().hex[:8]}@example.com"


def build_lead(
    email: str | None = None,
    source: str = "test",
    ranking_score: float | None = None,
    ranking_explanation: str | None = None,
    last_ranked_at: datetime | None = None,
    assigned_to: str | None = None,
    routing_reason: str | None = None,
    last_routed_at: datetime | None = None,
    lead_id: UUID | None = None,
    created_at: datetime | None = None,
) -> Lead:
    return Lead(
        id=lead_id or uuid4(),
        email=email or _next_email(),
        source=source,
        ranking_score=ranking_score,
        ranking_explanation=ranking_explanation,
        last_ranked_at=last_ranked_at,
        assigned_to=assigned_to,
        routing_reason=routing_reason,
        last_routed_at=last_routed_at,
        created_at=created_at or datetime.now(timezone.utc),
    )


async def create_lead(session: AsyncSession, **overrides: Any) -> Lead:
    lead = build_lead(**overrides)
    session.add(lead)
    await session.commit()
    await session.refresh(lead)
    return lead


async def create_leads(session: AsyncSession, count: int, **overrides: Any) -> list[Lead]:
    return [await create_lead(session, **overrides) for _ in range(count)]
