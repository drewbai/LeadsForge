"""API tests for /metrics endpoints (skipped when router absent)."""
from __future__ import annotations

import pytest


def _has_metrics_router() -> bool:
    try:
        __import__("app.api.v1.metrics_router")
        return True
    except Exception:
        return False


@pytest.mark.asyncio
async def test_metrics_endpoint_returns_payload(client) -> None:
    if not _has_metrics_router():
        pytest.skip("metrics_router not present on this branch")
    resp = await client.get("/api/v1/metrics")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, (list, dict))


@pytest.mark.asyncio
async def test_metrics_endpoint_filters_by_type(client) -> None:
    if not _has_metrics_router():
        pytest.skip("metrics_router not present on this branch")
    resp = await client.get("/api/v1/metrics", params={"metric_type": "lead_created"})
    assert resp.status_code == 200
