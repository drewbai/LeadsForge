from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services.routing.engine import route_lead

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/routing", tags=["routing"])


@router.post("/{lead_id}/compute")
async def compute_routing(
    lead_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    result = await route_lead(session, lead_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {
        "lead_id": result["lead_id"],
        "assigned_to": result["assigned_to"],
        "reason": result["reason"],
        "last_routed_at": result["last_routed_at"],
    }
