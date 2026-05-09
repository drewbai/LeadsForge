from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services.metrics.service import get_metrics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])


def _parse_labels(labels: str | None) -> dict[str, Any] | None:
    if not labels:
        return None
    try:
        parsed = json.loads(labels)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"labels must be valid JSON: {exc}",
        ) from exc
    if not isinstance(parsed, dict):
        raise HTTPException(
            status_code=400,
            detail="labels must decode to a JSON object",
        )
    return parsed


@router.get("")
async def list_metrics(
    metric_type: str | None = Query(default=None),
    labels: str | None = Query(
        default=None,
        description='JSON-encoded label filter, e.g. {"task_type":"rank_lead"}',
    ),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    parsed_labels = _parse_labels(labels)
    return await get_metrics(
        session,
        metric_type=metric_type,
        labels=parsed_labels,
        limit=limit,
        offset=offset,
    )
