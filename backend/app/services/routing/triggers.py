from __future__ import annotations

import logging
from uuid import UUID

logger = logging.getLogger(__name__)

ROUTING_TASK_TYPE = "route_lead"


async def enqueue_routing_recompute(lead_id: UUID | None) -> None:
    """Enqueue a ``route_lead`` task for the given lead via the canonical task engine.

    Symmetric with ``app.services.ranking.triggers.enqueue_ranking_recompute``:
    same defensive contract (no-op for None, swallow exceptions, log failures),
    same persistence semantics (writes a Task row that survives restarts and is
    visible at GET /api/v1/tasks/{id}).
    """
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
