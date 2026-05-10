"""Deterministic tests for app.services.routing.engine.route_lead.

Phase 74 lands routing as a real subsystem on dev, so the previous
``pytest.importorskip`` guards are removed; routing must be importable on
every CI run from this point forward.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from app.services.routing.engine import (
    RANKING_HIGH_THRESHOLD,
    RANKING_LOW_THRESHOLD,
    route_lead,
)

pytestmark = pytest.mark.asyncio


async def test_route_lead_high_score_yields_priority(db_session, seeded_lead) -> None:
    seeded_lead.ranking_score = RANKING_HIGH_THRESHOLD + 5.0
    db_session.add(seeded_lead)
    await db_session.commit()

    result = await route_lead(db_session, seeded_lead.id)
    assert result is not None
    assert result["assigned_to"] == "priority"
    assert "high score" in result["reason"]
    assert result["signals"]["ranking_score"] == pytest.approx(RANKING_HIGH_THRESHOLD + 5.0)


async def test_route_lead_mid_score_yields_standard(db_session, seeded_lead) -> None:
    seeded_lead.ranking_score = (RANKING_HIGH_THRESHOLD + RANKING_LOW_THRESHOLD) / 2.0
    db_session.add(seeded_lead)
    await db_session.commit()

    result = await route_lead(db_session, seeded_lead.id)
    assert result is not None
    assert result["assigned_to"] == "standard"
    assert "mid score" in result["reason"]


async def test_route_lead_low_score_yields_nurture(db_session, seeded_lead) -> None:
    seeded_lead.ranking_score = max(RANKING_LOW_THRESHOLD - 5.0, 0.0)
    db_session.add(seeded_lead)
    await db_session.commit()

    result = await route_lead(db_session, seeded_lead.id)
    assert result is not None
    assert result["assigned_to"] == "nurture"
    assert "low score" in result["reason"]


async def test_route_lead_persists_assignment_columns(db_session, seeded_lead) -> None:
    seeded_lead.ranking_score = RANKING_HIGH_THRESHOLD + 1.0
    db_session.add(seeded_lead)
    await db_session.commit()

    result = await route_lead(db_session, seeded_lead.id)
    assert result is not None

    await db_session.refresh(seeded_lead)
    assert seeded_lead.assigned_to == "priority"
    assert seeded_lead.routing_reason
    assert seeded_lead.last_routed_at is not None


async def test_route_lead_unknown_lead_returns_none(db_session) -> None:
    assert await route_lead(db_session, uuid4()) is None


async def test_route_lead_treats_missing_score_as_zero(db_session, seeded_lead) -> None:
    seeded_lead.ranking_score = None
    db_session.add(seeded_lead)
    await db_session.commit()

    result = await route_lead(db_session, seeded_lead.id)
    assert result is not None
    assert result["assigned_to"] == "nurture"
    assert result["signals"]["ranking_score"] == 0.0
