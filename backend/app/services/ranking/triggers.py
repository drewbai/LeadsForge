from __future__ import annotations

import logging
from uuid import UUID

logger = logging.getLogger(__name__)

RANKING_TASK_TYPE = "rank_lead"


async def enqueue_ranking_recompute(lead_id: UUID | None) -> None:
    """Enqueue a ``rank_lead`` task for the given lead via the canonical task engine.

    Safe to call from any async context. Opens its own short-lived session so
    callers (services, AI pipelines, ingestion) don't have to pass a session.
    Failures are logged, never raised — ranking recompute is a best-effort
    side-effect of the primary write.
    """
    if lead_id is None:
        return
    try:
        from app.db.engine import AsyncSessionLocal
        from app.services.tasks import enqueue as enqueue_task

        async with AsyncSessionLocal() as session:
            await enqueue_task(
                session,
                task_type=RANKING_TASK_TYPE,
                payload={"lead_id": str(lead_id)},
            )
    except Exception:
        logger.exception("Failed to enqueue rank_lead task for lead %s", lead_id)
