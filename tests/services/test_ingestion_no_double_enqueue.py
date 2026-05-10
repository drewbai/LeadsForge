"""Regression guard: ingestion must enqueue exactly ONE rank_lead task and ONE
route_lead task per lead.

Phase 73, as originally authored, triggered the ranking recompute in two places:
1. inside ``lead_service.create_lead`` (intentional)
2. inside ``ingestion/pipeline.run_ingestion`` after the create_lead return
   (accidental — this duplicated the trigger)

The Phase 73 integration patch removed the ingestion-side call. Phase 74 adds a
parallel routing trigger to ``lead_service.create_lead``; the same one-fire-per-
lead guarantee must hold for routing as well. This test fails loudly if anyone
re-introduces a duplicate trigger on either side.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from app.ingestion.models import IngestionLeadInput
from app.ingestion.pipeline import run_ingestion
from app.services import lead_service


@pytest.mark.asyncio
async def test_ingestion_enqueues_each_trigger_exactly_once_per_lead(db_session, monkeypatch) -> None:
    ranking_spy = AsyncMock(return_value=None)
    routing_spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", ranking_spy)
    monkeypatch.setattr(lead_service, "enqueue_routing_recompute", routing_spy)

    inputs = [IngestionLeadInput(email="ingest-1@example.com", source="signup")]
    results = await run_ingestion(inputs, db_session)

    assert results[0].success is True
    assert results[0].errors == []
    assert ranking_spy.await_count == 1
    assert routing_spy.await_count == 1


@pytest.mark.asyncio
async def test_ingestion_failed_validation_does_not_enqueue(db_session, monkeypatch) -> None:
    ranking_spy = AsyncMock(return_value=None)
    routing_spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", ranking_spy)
    monkeypatch.setattr(lead_service, "enqueue_routing_recompute", routing_spy)

    inputs = [IngestionLeadInput(email="ok@example.com", source="   ")]
    results = await run_ingestion(inputs, db_session)

    assert results[0].success is False
    assert "source is required" in results[0].errors
    ranking_spy.assert_not_called()
    routing_spy.assert_not_called()


@pytest.mark.asyncio
async def test_ingestion_three_leads_enqueues_three_of_each(db_session, monkeypatch) -> None:
    ranking_spy = AsyncMock(return_value=None)
    routing_spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", ranking_spy)
    monkeypatch.setattr(lead_service, "enqueue_routing_recompute", routing_spy)

    inputs = [IngestionLeadInput(email=f"batch-{i}@example.com", source="signup") for i in range(3)]
    results = await run_ingestion(inputs, db_session)

    assert all(r.success for r in results)
    assert ranking_spy.await_count == 3
    assert routing_spy.await_count == 3
