from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.models.lead import Lead
from app.services.routing.engine import route_lead

router = APIRouter(prefix="/api/v1/routing", tags=["routing"])


@router.post("/{lead_id}/route")
async def route_lead_now(
    lead_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Recompute and persist routing for a lead (synchronous; same logic as ``route_lead`` tasks)."""
    result = await route_lead(session, lead_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"lead_id": str(lead_id), "routing": result}


@router.get("/{lead_id}/status")
async def routing_status(
    lead_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    lead = await session.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {
        "lead_id": str(lead_id),
        "assigned_to": lead.assigned_to,
        "routing_reason": lead.routing_reason,
        "last_routed_at": (lead.last_routed_at.isoformat() if lead.last_routed_at else None),
        "ranking_score": lead.ranking_score,
    }
