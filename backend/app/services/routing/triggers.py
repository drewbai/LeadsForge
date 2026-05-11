from __future__ import annotations

import logging
from uuid import UUID

logger = logging.getLogger(__name__)

ROUTING_TASK_TYPE = "route_lead"


async def enqueue_route_lead(lead_id: UUID | None) -> None:
    """Enqueue a ``route_lead`` task (Phase 82 — after ranking or manual re-route)."""
    if lead_id is None:
        return
    try:
        from app.db.engine import AsyncSessionLocal
        from app.services.tasks import enqueue as enqueue_task

        async with AsyncSessionLocal() as session:
            await enqueue_task(
                session,
                task_type=ROUTING_TASK_TYPE,
                payload={"lead_id": str(lead_id)},
            )
    except Exception:
        logger.exception("Failed to enqueue route_lead task for lead %s", lead_id)


async def enqueue_routing_recompute(lead_id: UUID | None) -> None:
    """Best-effort route enqueue; alias for call sites that predate ``enqueue_route_lead``."""
    await enqueue_route_lead(lead_id)
