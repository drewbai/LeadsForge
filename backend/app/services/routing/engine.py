from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import AsyncSessionLocal
from app.models.lead import Lead
from app.models.metric import METRIC_LEAD_ROUTED
from app.services.metrics.service import fire_and_forget_increment

logger = logging.getLogger(__name__)

# Score thresholds for simple rules-based routing (Phase 81).
HIGH_VALUE_THRESHOLD = 90.0
MEDIUM_VALUE_THRESHOLD = 70.0


async def _record_routed_event(session: AsyncSession, lead_id: UUID, decision: dict[str, Any]) -> None:
    try:
        from app.services.events.activity import record_activity_event

        payload = {k: v for k, v in decision.items() if k != "lead_id"}
        await record_activity_event(
            session=session,
            lead_id=lead_id,
            event_type="lead.routed",
            payload=payload,
            performed_by="routing_engine",
        )
    except Exception:
        logger.exception("Failed to record lead.routed for lead %s", lead_id)


async def route_lead(session: AsyncSession, lead_id: UUID) -> dict[str, Any] | None:
    """Compute a routing decision, persist queue fields on ``Lead``, activity, and metrics."""
    result = await session.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if lead is None:
        return None

    score = lead.ranking_score
    decision: dict[str, Any]
    if score is None:
        decision = {
            "lead_id": str(lead_id),
            "routing_reason": "awaiting_rank",
            "assigned_to": None,
        }
    elif score >= HIGH_VALUE_THRESHOLD:
        bucket = "tier1_sdr"
        reason = "high_value"
        logger.debug("Routed lead %s score=%s -> %s (%s)", lead_id, score, bucket, reason)
        decision = {
            "lead_id": str(lead_id),
            "routing_reason": reason,
            "assigned_to": bucket,
            "ranking_score": score,
        }
    elif score >= MEDIUM_VALUE_THRESHOLD:
        bucket = "tier2_sdr"
        reason = "medium_value"
        logger.debug("Routed lead %s score=%s -> %s (%s)", lead_id, score, bucket, reason)
        decision = {
            "lead_id": str(lead_id),
            "routing_reason": reason,
            "assigned_to": bucket,
            "ranking_score": score,
        }
    else:
        bucket = "nurture_pool"
        reason = "standard"
        logger.debug("Routed lead %s score=%s -> %s (%s)", lead_id, score, bucket, reason)
        decision = {
            "lead_id": str(lead_id),
            "routing_reason": reason,
            "assigned_to": bucket,
            "ranking_score": score,
        }

    now = datetime.now(timezone.utc)
    lead.assigned_to = decision.get("assigned_to")
    lead.routing_reason = str(decision["routing_reason"])
    lead.last_routed_at = now
    await session.commit()

    await fire_and_forget_increment(
        METRIC_LEAD_ROUTED,
        {
            "lead_id": str(lead_id),
            "routing_reason": str(decision["routing_reason"]),
            "assigned_to": decision.get("assigned_to") or "",
        },
    )

    await _record_routed_event(session, lead_id, decision)
    return decision


async def trigger_routing(lead_id: UUID) -> None:
    """Synchronous-style trigger used by ingestion hooks; opens its own session."""
    async with AsyncSessionLocal() as session:
        await route_lead(session, lead_id)
