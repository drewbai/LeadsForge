from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import AsyncSessionLocal
from app.models.lead import Lead

logger = logging.getLogger(__name__)

# Score thresholds for simple rules-based routing (Phase 81).
HIGH_VALUE_THRESHOLD = 90.0
MEDIUM_VALUE_THRESHOLD = 70.0


async def route_lead(session: AsyncSession, lead_id: UUID) -> dict[str, Any] | None:
    """Assign a synthetic queue label from ranking score; no ORM columns required."""
    result = await session.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if lead is None:
        return None

    score = lead.ranking_score
    if score is None:
        return {
            "lead_id": str(lead_id),
            "routing_reason": "awaiting_rank",
            "assigned_to": None,
        }
    if score >= HIGH_VALUE_THRESHOLD:
        bucket = "tier1_sdr"
        reason = "high_value"
    elif score >= MEDIUM_VALUE_THRESHOLD:
        bucket = "tier2_sdr"
        reason = "medium_value"
    else:
        bucket = "nurture_pool"
        reason = "standard"

    logger.debug("Routed lead %s score=%s -> %s (%s)", lead_id, score, bucket, reason)
    return {
        "lead_id": str(lead_id),
        "routing_reason": reason,
        "assigned_to": bucket,
        "ranking_score": score,
    }


async def trigger_routing(lead_id: UUID) -> None:
    """Synchronous-style trigger used by ingestion hooks; opens its own session."""
    async with AsyncSessionLocal() as session:
        await route_lead(session, lead_id)
