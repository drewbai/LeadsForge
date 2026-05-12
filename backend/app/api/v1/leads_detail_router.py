from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.schemas.lead import LeadRead
from app.services import lead_service
from app.services.events.activity import record_activity_event

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/leads", tags=["leads-detail"])


class ActivityItem(BaseModel):
    id: str
    lead_id: str
    created_at: str
    activity_type: str
    activity_details: str | None
    performed_by: str | None


class ActivityListResponse(BaseModel):
    items: list[ActivityItem]


class ActivityNoteCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)


@router.get("/{lead_id}/activity", response_model=ActivityListResponse)
async def list_lead_activity(
    lead_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> ActivityListResponse:
    lead = await lead_service.get_lead(session, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    try:
        result = await session.execute(
            text(
                """
                SELECT id, lead_id, created_at, activity_type, activity_details, performed_by
                FROM lead_activity_log
                WHERE lead_id = :lid
                ORDER BY created_at DESC
                LIMIT 200
                """
            ),
            {"lid": lead_id},
        )
        rows = result.mappings().all()
    except Exception:
        logger.exception("list_lead_activity failed for lead_id=%s", lead_id)
        await session.rollback()
        return ActivityListResponse(items=[])

    items: list[ActivityItem] = []
    for r in rows:
        ca = r["created_at"]
        items.append(
            ActivityItem(
                id=str(r["id"]),
                lead_id=str(r["lead_id"]),
                created_at=ca.isoformat() if hasattr(ca, "isoformat") else str(ca),
                activity_type=str(r["activity_type"]),
                activity_details=r["activity_details"],
                performed_by=r["performed_by"],
            )
        )
    return ActivityListResponse(items=items)


@router.post("/{lead_id}/activity", status_code=status.HTTP_201_CREATED)
async def create_lead_activity_note(
    lead_id: UUID,
    body: ActivityNoteCreate,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    lead = await lead_service.get_lead(session, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    note_text = body.text.strip()
    if not note_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Note text is required")
    await record_activity_event(
        session,
        lead_id,
        "note.created",
        {"text": note_text},
        performed_by="ui",
        activity_details=note_text,
    )
    return {"status": "created"}


@router.get("/{lead_id}", response_model=LeadRead)
async def get_lead_v1(
    lead_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> LeadRead:
    lead = await lead_service.get_lead(session, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return LeadRead.model_validate(lead)
