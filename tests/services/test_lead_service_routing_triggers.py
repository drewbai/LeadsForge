"""Verifies lead_service trigger wiring (ranking on create; routing on update).

Routing after create is driven by the ranking pipeline (``compute_lead_ranking``),
not by ``create_lead`` directly.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from app.schemas.lead import LeadCreate
from app.services import lead_service


@pytest.mark.asyncio
async def test_create_lead_does_not_enqueue_routing_directly(db_session, monkeypatch) -> None:
    """``route_lead`` is enqueued after rank completes, not from create_lead."""
    routing_spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_routing_recompute", routing_spy)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", AsyncMock(return_value=None))
    monkeypatch.setattr(lead_service, "fire_and_forget_increment", AsyncMock(return_value=None))
    monkeypatch.setattr(lead_service, "record_activity_event", AsyncMock(return_value=None))

    await lead_service.create_lead(
        db_session,
        LeadCreate(email="trigger-create-routing@example.com", source="signup"),
    )

    routing_spy.assert_not_called()


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
async def test_create_lead_enqueues_only_ranking_not_routing(db_session, monkeypatch) -> None:
    ranking_spy = AsyncMock(return_value=None)
    routing_spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", ranking_spy)
    monkeypatch.setattr(lead_service, "enqueue_routing_recompute", routing_spy)
    monkeypatch.setattr(lead_service, "fire_and_forget_increment", AsyncMock(return_value=None))
    monkeypatch.setattr(lead_service, "record_activity_event", AsyncMock(return_value=None))

    lead = await lead_service.create_lead(
        db_session,
        LeadCreate(email="fanout@example.com", source="signup"),
    )

    ranking_spy.assert_awaited_once_with(lead.id)
    routing_spy.assert_not_called()
