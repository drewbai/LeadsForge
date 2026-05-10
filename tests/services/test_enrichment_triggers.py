"""Tests for the optional ranking trigger embedded in enrichment_service.enrich_lead.

Phase 73 added an optional ``lead_id`` kwarg to ``enrich_lead``. When supplied,
and when enrichment actually changed the dict, a ``rank_lead`` task should be
enqueued. When omitted (the existing public API contract), no trigger fires.
"""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from app.services import enrichment_service


@pytest.mark.asyncio
async def test_enrich_lead_without_lead_id_does_not_enqueue(monkeypatch) -> None:
    spy = AsyncMock()
    monkeypatch.setattr(enrichment_service, "enqueue_ranking_recompute", spy)

    out = await enrichment_service.enrich_lead({"email": "alpha@example.com"})

    assert "email" in out
    spy.assert_not_called()


@pytest.mark.asyncio
async def test_enrich_lead_with_lead_id_enqueues_when_dict_changes(monkeypatch) -> None:
    spy = AsyncMock(return_value=None)
    monkeypatch.setattr(enrichment_service, "enqueue_ranking_recompute", spy)
    lead_id = uuid4()

    await enrichment_service.enrich_lead(
        {"email": "alpha@example.com"},
        lead_id=lead_id,
    )

    spy.assert_awaited_once_with(lead_id)


@pytest.mark.asyncio
async def test_enrich_lead_with_none_lead_id_does_not_enqueue(monkeypatch) -> None:
    spy = AsyncMock()
    monkeypatch.setattr(enrichment_service, "enqueue_ranking_recompute", spy)

    await enrichment_service.enrich_lead(
        {"email": "alpha@example.com"},
        lead_id=None,
    )

    spy.assert_not_called()
