from __future__ import annotations

import asyncio
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


async def _run_recompute(lead_id: UUID) -> None:
    from app.db.engine import AsyncSessionLocal
    from app.services.ranking.engine import compute_lead_ranking

    try:
        async with AsyncSessionLocal() as session:
            await compute_lead_ranking(session, lead_id)
    except Exception:
        logger.exception("Background ranking recompute failed for lead %s", lead_id)


async def enqueue_ranking_recompute(lead_id: UUID) -> None:
    if lead_id is None:
        return
    try:
        asyncio.create_task(_run_recompute(lead_id))
    except RuntimeError:
        try:
            await _run_recompute(lead_id)
        except Exception:
            logger.exception(
                "Inline ranking recompute failed for lead %s", lead_id
            )
