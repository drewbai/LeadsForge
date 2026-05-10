"""Regression guard: ingestion must enqueue exactly ONE rank_lead task per lead.

Phase 73, as originally authored, triggered the ranking recompute in two places:
1. inside ``lead_service.create_lead`` (intentional)
2. inside ``ingestion/pipeline.run_ingestion`` after the create_lead return
   (accidental — this duplicated the trigger)

The integration patch removed the ingestion-side call. This test fails if anyone
re-introduces it.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from app.ingestion.models import IngestionLeadInput
from app.ingestion.pipeline import run_ingestion
from app.services import lead_service


@pytest.mark.asyncio
async def test_ingestion_enqueues_exactly_once_per_lead(db_session, monkeypatch) -> None:
    spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", spy)

    inputs = [IngestionLeadInput(email="ingest-1@example.com", source="signup")]
    results = await run_ingestion(inputs, db_session)

    assert results[0].success is True
    assert results[0].errors == []
    assert spy.await_count == 1


@pytest.mark.asyncio
async def test_ingestion_failed_validation_does_not_enqueue(db_session, monkeypatch) -> None:
    spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", spy)

    inputs = [IngestionLeadInput(email="not-an-email", source="signup")]
    results = await run_ingestion(inputs, db_session)

    assert results[0].success is False
    spy.assert_not_called()


@pytest.mark.asyncio
async def test_ingestion_three_leads_enqueues_three_tasks(db_session, monkeypatch) -> None:
    spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", spy)

    inputs = [IngestionLeadInput(email=f"batch-{i}@example.com", source="signup") for i in range(3)]
    results = await run_ingestion(inputs, db_session)

    assert all(r.success for r in results)
    assert spy.await_count == 3
