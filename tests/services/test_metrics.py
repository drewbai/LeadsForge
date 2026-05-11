"""Tests for the metrics service (Phase 78)."""

from __future__ import annotations

import asyncio

import pytest
from app.services.metrics import service as metrics_service


@pytest.mark.asyncio
async def test_increment_records_metric(db_session) -> None:
    await metrics_service.increment(db_session, "lead_created", labels={"source": "test"})
    payload = await metrics_service.get_metrics(db_session, metric_type="lead_created")
    assert payload["total"] >= 1
    assert payload["results"], "expected at least one metric row"
    assert payload["results"][0]["labels"] == {"source": "test"}


@pytest.mark.asyncio
async def test_record_writes_value(db_session) -> None:
    await metrics_service.record(
        db_session,
        metric_type="ranking_score",
        value=87.5,
        labels={"lead_id": "x"},
    )
    payload = await metrics_service.get_metrics(db_session, metric_type="ranking_score")
    assert payload["total"] == 1
    row = payload["results"][0]
    assert row["value"] == 87.5
    assert row["labels"] == {"lead_id": "x"}


@pytest.mark.asyncio
async def test_get_metrics_filters_by_type(db_session) -> None:
    await metrics_service.increment(db_session, "lead_created")
    await metrics_service.increment(db_session, "lead_enriched")
    only_created = await metrics_service.get_metrics(db_session, metric_type="lead_created")
    only_enriched = await metrics_service.get_metrics(db_session, metric_type="lead_enriched")
    assert all(r["metric_type"] == "lead_created" for r in only_created["results"])
    assert all(r["metric_type"] == "lead_enriched" for r in only_enriched["results"])


@pytest.mark.asyncio
async def test_get_metrics_filters_by_labels(db_session) -> None:
    await metrics_service.increment(db_session, "task_completed", labels={"task_type": "rank_lead"})
    await metrics_service.increment(db_session, "task_completed", labels={"task_type": "enrich"})
    filtered = await metrics_service.get_metrics(
        db_session,
        metric_type="task_completed",
        labels={"task_type": "rank_lead"},
    )
    assert filtered["total"] == 1
    assert filtered["results"][0]["labels"] == {"task_type": "rank_lead"}


@pytest.mark.asyncio
async def test_get_metrics_pagination(db_session) -> None:
    for i in range(3):
        await metrics_service.increment(db_session, "pagination_metric", labels={"i": i})
    page0 = await metrics_service.get_metrics(db_session, metric_type="pagination_metric", limit=2, offset=0)
    page1 = await metrics_service.get_metrics(db_session, metric_type="pagination_metric", limit=2, offset=2)
    assert page0["total"] == 3
    assert len(page0["results"]) == 2
    assert len(page1["results"]) == 1


@pytest.mark.asyncio
async def test_record_rejects_empty_metric_type(db_session) -> None:
    with pytest.raises(ValueError, match="metric_type"):
        await metrics_service.record(db_session, "   ", value=1.0)


@pytest.mark.asyncio
async def test_fire_and_forget_increment_persists(session_factory, monkeypatch) -> None:
    monkeypatch.setattr("app.db.engine.AsyncSessionLocal", session_factory)
    await metrics_service.fire_and_forget_increment("ff_lead_created", {"route": "test"})
    for _ in range(5):
        await asyncio.sleep(0)
        async with session_factory() as session:
            payload = await metrics_service.get_metrics(session, metric_type="ff_lead_created")
            if payload["total"] >= 1:
                assert payload["results"][0]["labels"] == {"route": "test"}
                return
    pytest.fail("background metric write did not appear")
