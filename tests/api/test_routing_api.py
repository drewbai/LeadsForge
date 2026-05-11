"""API tests for /api/v1/routing (Phase 84)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_post_route_returns_routing_decision(client, db_session, seeded_lead, monkeypatch) -> None:
    monkeypatch.setattr("app.services.routing.engine.fire_and_forget_increment", AsyncMock())

    seeded_lead.ranking_score = 91.0
    db_session.add(seeded_lead)
    await db_session.commit()

    with patch("app.services.events.activity.record_activity_event", new=AsyncMock()):
        resp = await client.post(f"/api/v1/routing/{seeded_lead.id}/route")

    assert resp.status_code == 200
    body = resp.json()
    assert body["lead_id"] == str(seeded_lead.id)
    assert body["routing"]["assigned_to"] == "tier1_sdr"
    assert body["routing"]["routing_reason"] == "high_value"


@pytest.mark.asyncio
async def test_post_route_404_for_unknown_lead(client) -> None:
    rid = uuid4()
    resp = await client.post(f"/api/v1/routing/{rid}/route")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_routing_status_reflects_db(client, db_session, seeded_lead, monkeypatch) -> None:
    monkeypatch.setattr("app.services.routing.engine.fire_and_forget_increment", AsyncMock())

    seeded_lead.ranking_score = 55.0
    db_session.add(seeded_lead)
    await db_session.commit()

    with patch("app.services.events.activity.record_activity_event", new=AsyncMock()):
        post = await client.post(f"/api/v1/routing/{seeded_lead.id}/route")
    assert post.status_code == 200

    resp = await client.get(f"/api/v1/routing/{seeded_lead.id}/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["assigned_to"] == "nurture_pool"
    assert body["routing_reason"] == "standard"
    assert body["ranking_score"] == 55.0
    assert body["last_routed_at"] is not None


@pytest.mark.asyncio
async def test_get_routing_status_404_for_unknown_lead(client) -> None:
    resp = await client.get(f"/api/v1/routing/{uuid4()}/status")
    assert resp.status_code == 404
