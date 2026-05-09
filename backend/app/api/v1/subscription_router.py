from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.services.subscriptions.service import (
    SubscriptionValidationError,
    create_subscription,
    deactivate_subscription,
    get_subscriptions,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/subscriptions", tags=["subscriptions"])


@router.post("", status_code=201)
async def create_subscription_endpoint(
    body: dict[str, Any] = Body(...),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    event_type = body.get("event_type")
    target_type = body.get("target_type")
    target = body.get("target")
    is_active = bool(body.get("is_active", True))

    if not event_type or not isinstance(event_type, str):
        raise HTTPException(status_code=400, detail="event_type is required")
    if not target_type or not isinstance(target_type, str):
        raise HTTPException(status_code=400, detail="target_type is required")
    if not target or not isinstance(target, str):
        raise HTTPException(status_code=400, detail="target is required")

    try:
        return await create_subscription(
            session=session,
            event_type=event_type,
            target_type=target_type,
            target=target,
            is_active=is_active,
        )
    except SubscriptionValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("")
async def list_subscriptions_endpoint(
    event_type: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    is_active: bool | None = Query(default=True),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    try:
        items = await get_subscriptions(
            session=session,
            event_type=event_type,
            target_type=target_type,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )
    except SubscriptionValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"items": items, "count": len(items), "limit": limit, "offset": offset}


@router.post("/{subscription_id}/deactivate")
async def deactivate_subscription_endpoint(
    subscription_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    result = await deactivate_subscription(session, subscription_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return result
