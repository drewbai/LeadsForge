"""API tests for /api/v1/routing/{lead_id}/compute (Phase 74).

The compute endpoint is intentionally synchronous (an explicit "route now"
action), so it must invoke route_lead immediately and return its result.
404 is returned for unknown leads.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from app.services.routing.engine import RANKING_HIGH_THRESHOLD

pytestmark = pytest.mark.asyncio


async def test_compute_routing_returns_assignment_for_known_lead(client, seeded_lead, db_session):
    seeded_lead.ranking_score = RANKING_HIGH_THRESHOLD + 5.0
    db_session.add(seeded_lead)
    await db_session.commit()

    resp = await client.post(f"/api/v1/routing/{seeded_lead.id}/compute")
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["lead_id"] == str(seeded_lead.id)
    assert body["assigned_to"] == "priority"
    assert body["reason"]
    assert body["last_routed_at"]


async def test_compute_routing_unknown_lead_returns_404(client) -> None:
    resp = await client.post(f"/api/v1/routing/{uuid4()}/compute")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Lead not found"


async def test_compute_routing_persists_columns(client, seeded_lead, db_session) -> None:
    seeded_lead.ranking_score = 10.0
    db_session.add(seeded_lead)
    await db_session.commit()

    resp = await client.post(f"/api/v1/routing/{seeded_lead.id}/compute")
    assert resp.status_code == 200

    await db_session.refresh(seeded_lead)
    assert seeded_lead.assigned_to == "nurture"
    assert seeded_lead.routing_reason
    assert seeded_lead.last_routed_at is not None
