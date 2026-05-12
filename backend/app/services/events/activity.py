from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import MetaData, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.sync_reflection import reflect_bind
from app.services.subscriptions import dispatcher

logger = logging.getLogger(__name__)


async def record_activity_event(
    session: AsyncSession,
    lead_id: UUID,
    event_type: str,
    payload: dict[str, Any] | None = None,
    performed_by: str | None = None,
    *,
    activity_details: str | None = None,
) -> dict[str, Any]:
    """Persist an ActivityEvent row into ``lead_activity_log`` and dispatch.

    This is the central hook used by services to record domain events. After
    the event is saved, the configured subscription dispatcher is invoked
    (fire-and-forget) so that webhook/email/internal subscribers are notified.
    """
    payload = payload or {}
    metadata = MetaData()
    await session.run_sync(lambda s: reflect_bind(metadata, s))
    activity_table = metadata.tables.get("lead_activity_log")

    event_id = uuid4()
    created_at = datetime.now(timezone.utc)

    details_value: str | None
    if activity_details is not None:
        details_value = activity_details
    else:
        details_value = str(payload) if payload else None

    if activity_table is not None:
        try:
            await session.execute(
                insert(activity_table).values(
                    id=event_id,
                    lead_id=lead_id,
                    activity_type=event_type,
                    activity_details=details_value,
                    performed_by=performed_by,
                )
            )
            await session.commit()
        except Exception:
            logger.exception(
                "Failed to persist ActivityEvent event_type=%s lead_id=%s",
                event_type,
                lead_id,
            )
    else:
        logger.debug(
            "lead_activity_log table not present; skipping persistence for %s",
            event_type,
        )

    event_payload: dict[str, Any] = {
        "lead_id": str(lead_id),
        "event_id": str(event_id),
        "created_at": created_at.isoformat(),
        "performed_by": performed_by,
        **payload,
    }

    try:
        dispatcher.fire_and_forget_dispatch(event_type, event_payload)
    except Exception:
        logger.exception(
            "Failed to dispatch ActivityEvent event_type=%s lead_id=%s",
            event_type,
            lead_id,
        )

    return {
        "event_id": str(event_id),
        "event_type": event_type,
        "lead_id": str(lead_id),
        "created_at": created_at.isoformat(),
    }
