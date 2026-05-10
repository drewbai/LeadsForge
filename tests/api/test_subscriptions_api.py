"""API tests for /api/v1/subscriptions endpoints."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_create_subscription_endpoint(client) -> None:
    resp = await client.post(
        "/api/v1/subscriptions",
        json={
            "event_type": "lead.created",
            "target_type": "webhook",
            "target": "https://example.com/hook",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["event_type"] == "lead.created"
    assert body["target_type"] == "webhook"
    assert body["is_active"] is True


@pytest.mark.asyncio
async def test_list_subscriptions_filters_by_event_type(client) -> None:
    await client.post(
        "/api/v1/subscriptions",
        json={
            "event_type": "lead.created",
            "target_type": "webhook",
            "target": "https://a.example.com",
        },
    )
    await client.post(
        "/api/v1/subscriptions",
        json={
            "event_type": "lead.enriched",
            "target_type": "webhook",
            "target": "https://b.example.com",
        },
    )
    resp = await client.get("/api/v1/subscriptions", params={"event_type": "lead.created"})
    assert resp.status_code == 200
    body = resp.json()
    items = body["items"]
    assert all(item["event_type"] == "lead.created" for item in items)


@pytest.mark.asyncio
async def test_deactivate_subscription_endpoint(client) -> None:
    create = await client.post(
        "/api/v1/subscriptions",
        json={
            "event_type": "lead.created",
            "target_type": "internal",
            "target": "log",
        },
    )
    subscription_id = create.json()["id"]
    resp = await client.post(f"/api/v1/subscriptions/{subscription_id}/deactivate")
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


@pytest.mark.asyncio
async def test_create_subscription_validates_payload(client) -> None:
    resp = await client.post("/api/v1/subscriptions", json={"event_type": "x"})
    assert resp.status_code in (400, 422)
