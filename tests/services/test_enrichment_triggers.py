"""Tests for the optional ranking + routing triggers embedded in
enrichment_service.enrich_lead.

Phase 73 added an optional ``lead_id`` kwarg that fires ranking recompute when
enrichment actually changes the dict. Phase 74 extends the same conditional
to also fire routing recompute. Both must hold simultaneously.
"""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from app.services import enrichment_service


@pytest.mark.asyncio
async def test_enrich_lead_without_lead_id_does_not_enqueue(monkeypatch) -> None:
    ranking_spy = AsyncMock()
    routing_spy = AsyncMock()
    monkeypatch.setattr(enrichment_service, "enqueue_ranking_recompute", ranking_spy)
    monkeypatch.setattr(enrichment_service, "enqueue_routing_recompute", routing_spy)

    out = await enrichment_service.enrich_lead({"email": "alpha@example.com"})

    assert "email" in out
    ranking_spy.assert_not_called()
    routing_spy.assert_not_called()


@pytest.mark.asyncio
async def test_enrich_lead_with_lead_id_enqueues_when_dict_changes(monkeypatch) -> None:
    ranking_spy = AsyncMock(return_value=None)
    routing_spy = AsyncMock(return_value=None)
    monkeypatch.setattr(enrichment_service, "enqueue_ranking_recompute", ranking_spy)
    monkeypatch.setattr(enrichment_service, "enqueue_routing_recompute", routing_spy)
    lead_id = uuid4()

    await enrichment_service.enrich_lead(
        {"email": "alpha@example.com"},
        lead_id=lead_id,
    )

    ranking_spy.assert_awaited_once_with(lead_id)
    routing_spy.assert_awaited_once_with(lead_id)


@pytest.mark.asyncio
async def test_enrich_lead_with_none_lead_id_does_not_enqueue(monkeypatch) -> None:
    ranking_spy = AsyncMock()
    routing_spy = AsyncMock()
    monkeypatch.setattr(enrichment_service, "enqueue_ranking_recompute", ranking_spy)
    monkeypatch.setattr(enrichment_service, "enqueue_routing_recompute", routing_spy)

    await enrichment_service.enrich_lead(
        {"email": "alpha@example.com"},
        lead_id=None,
    )

    ranking_spy.assert_not_called()
    routing_spy.assert_not_called()
