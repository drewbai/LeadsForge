"""Tests for app.services.routing.engine (Phases 81–83)."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from app.services.routing import engine as routing_engine


@pytest.mark.asyncio
async def test_route_lead_assigns_priority_for_high_score(db_session, seeded_lead, monkeypatch) -> None:
    monkeypatch.setattr("app.services.routing.engine.fire_and_forget_increment", AsyncMock())
    seeded_lead.ranking_score = 95.0
    db_session.add(seeded_lead)
    await db_session.commit()

    result = await route_lead(db_session, seeded_lead.id)
    assert result is not None
    assert "assigned_to" in result or "routing_reason" in result
    assert result.get("assigned_to") == "tier1_sdr"
    await db_session.refresh(seeded_lead)
    assert seeded_lead.assigned_to == "tier1_sdr"
    assert seeded_lead.routing_reason == "high_value"
    assert seeded_lead.last_routed_at is not None


async def test_route_lead_unknown_lead_returns_none(db_session) -> None:
    result = await routing_engine.route_lead(db_session, uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_route_lead_records_activity_event(db_session, seeded_lead, monkeypatch) -> None:
    spy = AsyncMock()
    monkeypatch.setattr("app.services.events.activity.record_activity_event", spy)
    monkeypatch.setattr(
        "app.services.routing.engine.fire_and_forget_increment",
        AsyncMock(),
    )
    seeded_lead.ranking_score = 72.0
    db_session.add(seeded_lead)
    await db_session.commit()

    await routing_engine.route_lead(db_session, seeded_lead.id)

    spy.assert_awaited_once()
    call_kw = spy.call_args.kwargs
    assert call_kw["event_type"] == "lead.routed"
    assert call_kw["lead_id"] == seeded_lead.id
    assert "assigned_to" in call_kw["payload"]


@pytest.mark.asyncio
async def test_trigger_routing_is_idempotent(seeded_lead, session_factory, monkeypatch) -> None:
    from app.services.routing import engine as re

    monkeypatch.setattr(re, "AsyncSessionLocal", session_factory)
    monkeypatch.setattr(re, "fire_and_forget_increment", AsyncMock())
    await re.trigger_routing(seeded_lead.id)
    await re.trigger_routing(seeded_lead.id)
