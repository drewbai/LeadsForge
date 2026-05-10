"""API tests for GET /api/v1/metrics (Phase 78)."""

from __future__ import annotations

import json

import pytest
from app.services.metrics import service as metrics_service


@pytest.mark.asyncio
async def test_metrics_endpoint_payload_shape_empty(client) -> None:
    resp = await client.get("/api/v1/metrics")
    assert resp.status_code == 200
    body = resp.json()
    assert body["results"] == []
    assert body["total"] == 0
    assert body["limit"] == 100
    assert body["offset"] == 0
    assert body["filters"] == {"metric_type": None, "labels": None}


@pytest.mark.asyncio
async def test_metrics_endpoint_lists_rows(client, db_session) -> None:
    await metrics_service.increment(db_session, "lead_created", labels={"source": "signup"})
    resp = await client.get("/api/v1/metrics", params={"metric_type": "lead_created"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    assert body["filters"] == {"metric_type": "lead_created", "labels": None}
    assert any(r["metric_type"] == "lead_created" for r in body["results"])


@pytest.mark.asyncio
async def test_metrics_endpoint_label_filter(client, db_session) -> None:
    await metrics_service.increment(db_session, "lead_enriched", labels={"provider": "a"})
    await metrics_service.increment(db_session, "lead_enriched", labels={"provider": "b"})
    labels = json.dumps({"provider": "a"})
    resp = await client.get("/api/v1/metrics", params={"metric_type": "lead_enriched", "labels": labels})
    assert resp.status_code == 200
    body = resp.json()
    assert body["filters"]["labels"] == {"provider": "a"}
    assert body["total"] == 1
    assert body["results"][0]["labels"] == {"provider": "a"}


@pytest.mark.asyncio
async def test_metrics_endpoint_rejects_invalid_labels_json(client) -> None:
    resp = await client.get("/api/v1/metrics", params={"labels": "not-json"})
    assert resp.status_code == 400
    assert "labels" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_metrics_endpoint_rejects_non_object_labels(client) -> None:
    resp = await client.get("/api/v1/metrics", params={"labels": "[1,2]"})
    assert resp.status_code == 400
    assert "object" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_metrics_endpoint_validates_limit(client) -> None:
    resp = await client.get("/api/v1/metrics", params={"limit": 2000})
    assert resp.status_code == 422
