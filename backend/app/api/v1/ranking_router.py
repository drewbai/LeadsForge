from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services.ranking.engine import (
    compute_lead_ranking,
    recompute_ranking_for_all_leads,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ranking", tags=["ranking"])


@router.post("/{lead_id}/recompute")
async def recompute_ranking(
    lead_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    result = await compute_lead_ranking(session, lead_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return result


async def _recompute_all_task() -> None:
    async for session in get_session():
        try:
            await recompute_ranking_for_all_leads(session)
        except Exception:
            logger.exception("Background ranking recompute failed")
        finally:
            await session.close()
        break


@router.post("/recompute-all")
async def recompute_all(
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    background_tasks.add_task(_recompute_all_task)
    return {"status": "scheduled", "job": "recompute_all_rankings"}
