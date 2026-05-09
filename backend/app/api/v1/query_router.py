from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services.query.engine import search_leads

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/leads", tags=["leads-query"])


@router.get("/search")
async def search(
    text: str | None = Query(default=None, description="Free-text search"),
    tags: list[str] | None = Query(default=None, description="Filter by tag names"),
    min_score: float | None = Query(default=None, ge=0.0),
    max_score: float | None = Query(default=None, ge=0.0),
    assigned_to: str | None = Query(default=None),
    source: str | None = Query(default=None),
    sort_by: str | None = Query(default="created_at"),
    sort_dir: str | None = Query(default="desc"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    return await search_leads(
        session,
        text=text,
        tags=tags,
        min_score=min_score,
        max_score=max_score,
        assigned_to=assigned_to,
        source=source,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=limit,
        offset=offset,
    )
