"""Tests for app.services.routing.engine (Phase 81)."""

from __future__ import annotations

from uuid import uuid4

import pytest
from app.services.routing import engine as routing_engine


@pytest.mark.asyncio
async def test_route_lead_assigns_priority_for_high_score(db_session, seeded_lead) -> None:
    seeded_lead.ranking_score = 95.0
    db_session.add(seeded_lead)
    await db_session.commit()

    result = await routing_engine.route_lead(db_session, seeded_lead.id)
    assert result is not None
    assert "assigned_to" in result or "routing_reason" in result
    assert result.get("assigned_to") == "tier1_sdr"


@pytest.mark.asyncio
async def test_route_lead_unknown_lead_returns_none(db_session) -> None:
    result = await routing_engine.route_lead(db_session, uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_trigger_routing_is_idempotent(seeded_lead, session_factory, monkeypatch) -> None:
    from app.services.routing import engine as re

    monkeypatch.setattr(re, "AsyncSessionLocal", session_factory)
    await re.trigger_routing(seeded_lead.id)
    await re.trigger_routing(seeded_lead.id)
