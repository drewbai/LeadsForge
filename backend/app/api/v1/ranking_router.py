from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import MetaData, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.db.sync_reflection import reflect_bind
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


@router.get("/{lead_id}/status")
async def ranking_status(
    lead_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    metadata = MetaData()
    await session.run_sync(lambda s: reflect_bind(metadata, s))
    leads = metadata.tables.get("leads")
    if leads is None:
        raise HTTPException(status_code=500, detail="leads table not found")

    columns_to_select = [leads.c.id]
    if "ranking_score" in leads.c:
        columns_to_select.append(leads.c.ranking_score)
    if "last_ranked_at" in leads.c:
        columns_to_select.append(leads.c.last_ranked_at)

    result = await session.execute(select(*columns_to_select).where(leads.c.id == lead_id))
    row = result.mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Lead not found")

    last_ranked_at = row.get("last_ranked_at")
    return {
        "lead_id": str(lead_id),
        "ranking_score": row.get("ranking_score"),
        "last_ranked_at": (last_ranked_at.isoformat() if last_ranked_at is not None else None),
    }
