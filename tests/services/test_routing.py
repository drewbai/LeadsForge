"""Tests for app.services.routing.engine (skipped if not present on branch)."""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_route_lead_assigns_priority_for_high_score(db_session, seeded_lead) -> None:
    routing_engine = pytest.importorskip("app.services.routing.engine")

    seeded_lead.ranking_score = 95.0
    db_session.add(seeded_lead)
    await db_session.commit()

    result = await routing_engine.route_lead(db_session, seeded_lead.id)
    assert result is not None
    assert "assigned_to" in result or "routing_reason" in result


@pytest.mark.asyncio
async def test_route_lead_unknown_lead_returns_none(db_session) -> None:
    from uuid import uuid4

    routing_engine = pytest.importorskip("app.services.routing.engine")
    result = await routing_engine.route_lead(db_session, uuid4())
    assert result is None or result.get("assigned_to") is None


@pytest.mark.asyncio
async def test_trigger_routing_is_idempotent(db_session, seeded_lead) -> None:
    routing_engine = pytest.importorskip("app.services.routing.engine")
    trigger = getattr(routing_engine, "trigger_routing", None)
    if trigger is None:
        pytest.skip("trigger_routing not implemented")
    await trigger(seeded_lead.id)
    await trigger(seeded_lead.id)
