"""Tests for the subscription service and dispatcher."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.subscriptions import dispatcher
from app.services.subscriptions import service as subscription_service


@pytest.mark.asyncio
async def test_create_subscription_persists(db_session) -> None:
    sub = await subscription_service.create_subscription(
        db_session,
        event_type="lead.created",
        target_type="webhook",
        target="https://example.com/hook",
    )
    assert sub["event_type"] == "lead.created"
    assert sub["target_type"] == "webhook"
    assert sub["is_active"] is True
    assert sub["id"]


@pytest.mark.asyncio
async def test_get_subscriptions_filters_by_event_type(db_session) -> None:
    await subscription_service.create_subscription(db_session, "lead.created", "webhook", "https://a.example.com")
    await subscription_service.create_subscription(db_session, "lead.enriched", "webhook", "https://b.example.com")

    rows = await subscription_service.get_subscriptions(db_session, event_type="lead.created")
    assert len(rows) == 1
    assert rows[0]["event_type"] == "lead.created"


@pytest.mark.asyncio
async def test_deactivate_subscription_sets_inactive(db_session) -> None:
    created = await subscription_service.create_subscription(db_session, "lead.created", "internal", "log")
    result = await subscription_service.deactivate_subscription(db_session, created["id"])
    assert result is not None
    assert result["is_active"] is False


@pytest.mark.asyncio
async def test_create_subscription_rejects_invalid_target_type(db_session) -> None:
    with pytest.raises(subscription_service.SubscriptionValidationError):
        await subscription_service.create_subscription(db_session, "lead.created", "carrier-pigeon", "n/a")


@pytest.mark.asyncio
async def test_dispatcher_posts_to_webhook(db_session, patch_dispatcher_session) -> None:
    if patch_dispatcher_session is None:
        pytest.skip("subscription dispatcher not present")
    await subscription_service.create_subscription(db_session, "lead.created", "webhook", "https://example.com/hook")

    fake_response = MagicMock()
    fake_response.raise_for_status = MagicMock(return_value=None)

    fake_client = AsyncMock()
    fake_client.post = AsyncMock(return_value=fake_response)
    fake_client.__aenter__.return_value = fake_client
    fake_client.__aexit__.return_value = None

    with patch.object(dispatcher.httpx, "AsyncClient", return_value=fake_client):
        summary = await dispatcher.dispatch_event(db_session, "lead.created", {"lead_id": "abc"})

    assert summary["subscriber_count"] == 1
    assert summary["dispatched"] == 1
    assert summary["failed"] == 0
    fake_client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_dispatcher_records_failure_metric_on_webhook_error(db_session, patch_dispatcher_session) -> None:
    if patch_dispatcher_session is None:
        pytest.skip("subscription dispatcher not present")
    await subscription_service.create_subscription(db_session, "lead.created", "webhook", "https://example.com/hook")

    fake_client = AsyncMock()
    fake_client.post = AsyncMock(side_effect=RuntimeError("boom"))
    fake_client.__aenter__.return_value = fake_client
    fake_client.__aexit__.return_value = None

    with patch.object(dispatcher.httpx, "AsyncClient", return_value=fake_client):
        summary = await dispatcher.dispatch_event(db_session, "lead.created", {"lead_id": "abc"})

    assert summary["dispatched"] == 0
    assert summary["failed"] == 1


@pytest.mark.asyncio
async def test_dispatcher_invokes_internal_handler(db_session, patch_dispatcher_session) -> None:
    if patch_dispatcher_session is None:
        pytest.skip("subscription dispatcher not present")
    received: list[tuple[str, dict]] = []

    async def handler(event_type, payload):
        received.append((event_type, payload))

    dispatcher.register_internal_handler("test.handler", handler)
    try:
        await subscription_service.create_subscription(db_session, "lead.created", "internal", "test.handler")
        summary = await dispatcher.dispatch_event(db_session, "lead.created", {"lead_id": "xyz"})
    finally:
        dispatcher.unregister_internal_handler("test.handler")

    assert summary["dispatched"] == 1
    assert received and received[0][0] == "lead.created"
    assert received[0][1]["lead_id"] == "xyz"
