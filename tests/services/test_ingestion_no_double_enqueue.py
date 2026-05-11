"""Regression guard: ingestion must enqueue exactly one rank per lead from create_lead.

``route_lead`` is scheduled by the ranking engine after scores are computed, not from
``create_lead``; this test still guards against duplicate *rank* triggers in ingestion.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from app.ingestion.models import IngestionLeadInput
from app.ingestion.pipeline import run_ingestion
from app.services import lead_service


@pytest.mark.asyncio
async def test_ingestion_enqueues_ranking_once_per_lead(db_session, monkeypatch) -> None:
    ranking_spy = AsyncMock(return_value=None)
    routing_spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", ranking_spy)
    monkeypatch.setattr(lead_service, "enqueue_routing_recompute", routing_spy)
    monkeypatch.setattr(lead_service, "fire_and_forget_increment", AsyncMock(return_value=None))
    monkeypatch.setattr(lead_service, "record_activity_event", AsyncMock(return_value=None))

    inputs = [IngestionLeadInput(email="ingest-1@example.com", source="signup")]
    results = await run_ingestion(inputs, db_session)

    assert results[0].success is True
    assert results[0].errors == []
    assert ranking_spy.await_count == 1
    routing_spy.assert_not_called()


@pytest.mark.asyncio
async def test_ingestion_failed_validation_does_not_enqueue(db_session, monkeypatch) -> None:
    ranking_spy = AsyncMock(return_value=None)
    routing_spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", ranking_spy)
    monkeypatch.setattr(lead_service, "enqueue_routing_recompute", routing_spy)
    monkeypatch.setattr(lead_service, "fire_and_forget_increment", AsyncMock(return_value=None))
    monkeypatch.setattr(lead_service, "record_activity_event", AsyncMock(return_value=None))

    inputs = [IngestionLeadInput(email="ok@example.com", source="   ")]
    results = await run_ingestion(inputs, db_session)

    assert results[0].success is False
    assert "source is required" in results[0].errors
    ranking_spy.assert_not_called()
    routing_spy.assert_not_called()


@pytest.mark.asyncio
async def test_ingestion_three_leads_enqueues_three_ranks(db_session, monkeypatch) -> None:
    ranking_spy = AsyncMock(return_value=None)
    routing_spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", ranking_spy)
    monkeypatch.setattr(lead_service, "enqueue_routing_recompute", routing_spy)
    monkeypatch.setattr(lead_service, "fire_and_forget_increment", AsyncMock(return_value=None))
    monkeypatch.setattr(lead_service, "record_activity_event", AsyncMock(return_value=None))

    inputs = [IngestionLeadInput(email=f"batch-{i}@example.com", source="signup") for i in range(3)]
    results = await run_ingestion(inputs, db_session)

    assert all(r.success for r in results)
    assert ranking_spy.await_count == 3
    routing_spy.assert_not_called()
