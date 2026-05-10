"""Verifies lead_service trigger wiring (routing recompute on create/update).

Mirrors tests/services/test_lead_service_triggers.py for the routing trigger.
Each create/update fans out to *both* a ranking task and a routing task; both
sets of fan-out tests must hold simultaneously.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from app.schemas.lead import LeadCreate
from app.services import lead_service


@pytest.mark.asyncio
async def test_create_lead_enqueues_routing_once(db_session, monkeypatch) -> None:
    routing_spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_routing_recompute", routing_spy)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", AsyncMock(return_value=None))

    lead = await lead_service.create_lead(
        db_session,
        LeadCreate(email="trigger-create-routing@example.com", source="signup"),
    )

    routing_spy.assert_awaited_once_with(lead.id)


@pytest.mark.asyncio
async def test_update_lead_enqueues_routing_once(db_session, seeded_lead, monkeypatch) -> None:
    routing_spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_routing_recompute", routing_spy)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", AsyncMock(return_value=None))

    updated = await lead_service.update_lead(
        db_session,
        seeded_lead.id,
        LeadCreate(email="trigger-update-routing@example.com", source="manual"),
    )

    assert updated is not None
    assert updated.email == "trigger-update-routing@example.com"
    routing_spy.assert_awaited_once_with(seeded_lead.id)


@pytest.mark.asyncio
async def test_update_lead_missing_does_not_enqueue_routing(db_session, monkeypatch) -> None:
    from uuid import uuid4

    routing_spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_routing_recompute", routing_spy)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", AsyncMock(return_value=None))

    result = await lead_service.update_lead(
        db_session,
        uuid4(),
        LeadCreate(email="ghost-routing@example.com", source="manual"),
    )

    assert result is None
    routing_spy.assert_not_called()


@pytest.mark.asyncio
async def test_delete_lead_does_not_enqueue_routing(db_session, seeded_lead, monkeypatch) -> None:
    routing_spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_routing_recompute", routing_spy)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", AsyncMock(return_value=None))

    ok = await lead_service.delete_lead(db_session, seeded_lead.id)

    assert ok is True
    routing_spy.assert_not_called()


@pytest.mark.asyncio
async def test_create_lead_fans_out_ranking_and_routing(db_session, monkeypatch) -> None:
    """Regression guard: a single create must fan out to *both* triggers, not one."""
    ranking_spy = AsyncMock(return_value=None)
    routing_spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", ranking_spy)
    monkeypatch.setattr(lead_service, "enqueue_routing_recompute", routing_spy)

    lead = await lead_service.create_lead(
        db_session,
        LeadCreate(email="fanout@example.com", source="signup"),
    )

    ranking_spy.assert_awaited_once_with(lead.id)
    routing_spy.assert_awaited_once_with(lead.id)
