"""API tests for /api/v1/health and /api/v1/readiness."""
from __future__ import annotations

import pytest


def _has_v1_health_router() -> bool:
    try:
        __import__("app.api.v1.health_router")
        return True
    except Exception:
        return False


@pytest.mark.asyncio
async def test_legacy_health_endpoint(client) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"health": "ok"}


@pytest.mark.asyncio
async def test_v1_health_endpoint(client, patch_health_session) -> None:
    if not _has_v1_health_router():
        pytest.skip("v1 health router not present on this branch")
    resp = await client.get("/api/v1/health")
    assert resp.status_code in (200, 503)
    body = resp.json()
    assert "status" in body
    assert "version" in body
    assert "database" in body
    assert "tasks" in body
    assert "metrics" in body
    assert "subscriptions" in body
    assert "timestamp" in body


@pytest.mark.asyncio
async def test_v1_readiness_endpoint(client, patch_health_session) -> None:
    if not _has_v1_health_router():
        pytest.skip("v1 health router not present on this branch")
    resp = await client.get("/api/v1/readiness")
    assert resp.status_code in (200, 503)
    body = resp.json()
    assert "ready" in body
    assert "reasons" in body


@pytest.mark.asyncio
async def test_v1_health_reports_seeded_lead_counts(
    client, db_session, patch_health_session
) -> None:
    if not _has_v1_health_router():
        pytest.skip("v1 health router not present on this branch")
    from tests.factories.lead_factory import create_leads

    await create_leads(db_session, count=3)
    resp = await client.get("/api/v1/health")
    assert resp.status_code in (200, 503)
    body = resp.json()
    assert body["metrics"]["total_leads"] == 3
