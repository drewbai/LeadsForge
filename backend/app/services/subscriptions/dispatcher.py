from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import AsyncSessionLocal
from app.models.subscription import Subscription
from app.services.subscriptions.service import get_active_subscriptions_for_event

logger = logging.getLogger(__name__)


WEBHOOK_TIMEOUT_SECONDS = 10.0


InternalHandler = Callable[[str, dict[str, Any]], Awaitable[None]]

_INTERNAL_HANDLERS: dict[str, InternalHandler] = {}


def register_internal_handler(name: str, handler: InternalHandler) -> None:
    _INTERNAL_HANDLERS[name] = handler
    logger.info("Registered internal subscription handler '%s'", name)


def unregister_internal_handler(name: str) -> None:
    _INTERNAL_HANDLERS.pop(name, None)


async def _record_failure_metric(event_type: str, target_type: str) -> None:
    try:
        from app.services.metrics.service import fire_and_forget_increment

        await fire_and_forget_increment(
            "subscription_dispatch_failed",
            labels={"event_type": event_type, "target_type": target_type},
        )
    except Exception:
        logger.debug(
            "Metrics module unavailable; skipping failure metric for %s/%s",
            event_type,
            target_type,
        )


async def _record_failure_activity(
    session: AsyncSession,
    event_type: str,
    payload: dict[str, Any],
    error: str,
) -> None:
    try:
        from sqlalchemy import MetaData, insert

        metadata = MetaData()
        await session.run_sync(lambda sync_session: metadata.reflect(bind=sync_session.bind))
        activity_table = metadata.tables.get("lead_activity_log")
        if activity_table is None:
            return
        lead_id = payload.get("lead_id")
        if lead_id is None:
            return
        from uuid import uuid4

        await session.execute(
            insert(activity_table).values(
                id=uuid4(),
                lead_id=lead_id,
                activity_type="subscription_dispatch_failed",
                activity_details=f"event_type={event_type} error={error}",
                performed_by="system",
            )
        )
        await session.commit()
    except Exception:
        logger.debug("Failed to record dispatch failure activity event", exc_info=True)


async def _dispatch_webhook(
    subscription: Subscription,
    event_type: str,
    payload: dict[str, Any],
) -> None:
    body = {"event_type": event_type, "payload": payload}
    async with httpx.AsyncClient(timeout=WEBHOOK_TIMEOUT_SECONDS) as client:
        response = await client.post(subscription.target, json=body)
        response.raise_for_status()


async def _dispatch_email(
    subscription: Subscription,
    event_type: str,
    payload: dict[str, Any],
) -> None:
    logger.info(
        "[email-stub] would send to=%s event_type=%s payload_keys=%s",
        subscription.target,
        event_type,
        list(payload.keys()),
    )


async def _dispatch_internal(
    subscription: Subscription,
    event_type: str,
    payload: dict[str, Any],
) -> None:
    handler = _INTERNAL_HANDLERS.get(subscription.target)
    if handler is None:
        raise RuntimeError(f"No internal handler registered for '{subscription.target}'")
    await handler(event_type, payload)


async def _dispatch_to_subscription(
    session: AsyncSession,
    subscription: Subscription,
    event_type: str,
    payload: dict[str, Any],
) -> bool:
    try:
        if subscription.target_type == "webhook":
            await _dispatch_webhook(subscription, event_type, payload)
        elif subscription.target_type == "email":
            await _dispatch_email(subscription, event_type, payload)
        elif subscription.target_type == "internal":
            await _dispatch_internal(subscription, event_type, payload)
        else:
            logger.warning(
                "Unknown target_type '%s' for subscription %s",
                subscription.target_type,
                subscription.id,
            )
            return False
        return True
    except Exception as exc:
        logger.exception(
            "Subscription dispatch failed subscription_id=%s event_type=%s target_type=%s",
            subscription.id,
            event_type,
            subscription.target_type,
        )
        await _record_failure_metric(event_type, subscription.target_type)
        await _record_failure_activity(session, event_type, payload, str(exc))
        return False


async def dispatch_event(
    session: AsyncSession,
    event_type: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    subscriptions = await get_active_subscriptions_for_event(session, event_type)
    if not subscriptions:
        return {
            "event_type": event_type,
            "subscriber_count": 0,
            "dispatched": 0,
            "failed": 0,
        }

    results = await asyncio.gather(
        *[_dispatch_to_subscription(session, sub, event_type, payload) for sub in subscriptions],
        return_exceptions=False,
    )
    dispatched = sum(1 for r in results if r)
    failed = len(results) - dispatched
    return {
        "event_type": event_type,
        "subscriber_count": len(subscriptions),
        "dispatched": dispatched,
        "failed": failed,
    }


async def dispatch(event: dict[str, Any]) -> dict[str, Any]:
    """Convenience entry point matching the spec: dispatcher.dispatch(event).

    The event dict must contain at least 'event_type'. The remaining keys are
    forwarded to subscribers as the payload.
    """
    event_type = event.get("event_type")
    if not event_type:
        raise ValueError("event must include 'event_type'")
    payload = {k: v for k, v in event.items() if k != "event_type"}
    async with AsyncSessionLocal() as session:
        return await dispatch_event(session, event_type, payload)


async def _run_dispatch(event_type: str, payload: dict[str, Any]) -> None:
    try:
        async with AsyncSessionLocal() as session:
            await dispatch_event(session, event_type, payload)
    except Exception:
        logger.exception("Background dispatch failed for event_type=%s", event_type)


def fire_and_forget_dispatch(event_type: str, payload: dict[str, Any]) -> None:
    """Schedule a dispatch without blocking the caller. Safe to call from sync paths."""
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_run_dispatch(event_type, payload))
    except RuntimeError:
        asyncio.run(_run_dispatch(event_type, payload))
