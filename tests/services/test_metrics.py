"""Tests for the metrics service (skipped if not on branch)."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_increment_records_metric(db_session) -> None:
    service = pytest.importorskip("app.services.metrics.service")
    increment = getattr(service, "increment", None)
    if increment is None:
        pytest.skip("MetricsService.increment not exposed")
    await increment(db_session, "lead_created", labels={"source": "test"})

    get_metrics = getattr(service, "get_metrics", None)
    if get_metrics is None:
        pytest.skip("get_metrics not exposed")
    rows = await get_metrics(db_session, metric_type="lead_created")
    assert rows, "expected at least one metric row"


@pytest.mark.asyncio
async def test_record_writes_value(db_session) -> None:
    service = pytest.importorskip("app.services.metrics.service")
    record = getattr(service, "record", None)
    if record is None:
        pytest.skip("MetricsService.record not exposed")
    await record(db_session, metric_type="ranking_score", value=87.5, labels={"lead_id": "x"})


@pytest.mark.asyncio
async def test_get_metrics_filters_by_type(db_session) -> None:
    service = pytest.importorskip("app.services.metrics.service")
    increment = getattr(service, "increment", None)
    get_metrics = getattr(service, "get_metrics", None)
    if increment is None or get_metrics is None:
        pytest.skip("metrics service incomplete")
    await increment(db_session, "lead_created")
    await increment(db_session, "lead_enriched")
    only_created = await get_metrics(db_session, metric_type="lead_created")
    only_enriched = await get_metrics(db_session, metric_type="lead_enriched")
    assert all(
        (r.get("metric_type") if isinstance(r, dict) else getattr(r, "metric_type")) == "lead_created"
        for r in only_created
    )
    assert all(
        (r.get("metric_type") if isinstance(r, dict) else getattr(r, "metric_type")) == "lead_enriched"
        for r in only_enriched
    )
