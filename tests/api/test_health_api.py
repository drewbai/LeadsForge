"""API tests for /api/v1/health and /api/v1/readiness (Phase 80)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_legacy_health_endpoint(client) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"health": "ok"}


@pytest.mark.asyncio
async def test_v1_health_endpoint(client, patch_health_session) -> None:
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
async def test_v1_health_503_when_status_error(client, monkeypatch) -> None:
    import app.api.v1.health_router as health_router

    monkeypatch.setattr(
        health_router,
        "get_health",
        AsyncMock(
            return_value={
                "status": "error",
                "database": {"status": "error", "details": {}},
                "tasks": {"pending": 0, "running": 0, "recent_errors": 0},
                "metrics": {"total_leads": 0, "total_tasks": 0, "total_events": 0},
                "subscriptions": {"active": 0, "by_event_type": {}},
                "version": "test",
                "timestamp": "ts",
            },
        ),
    )
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 503
    assert resp.json()["status"] == "error"


@pytest.mark.asyncio
async def test_v1_readiness_endpoint(client, patch_health_session) -> None:
    resp = await client.get("/api/v1/readiness")
    assert resp.status_code in (200, 503)
    body = resp.json()
    assert "ready" in body
    assert "reasons" in body
    assert "migrations" in body
    assert "task_enqueue" in body


@pytest.mark.asyncio
async def test_v1_readiness_503_when_not_ready(client, monkeypatch) -> None:
    import app.api.v1.health_router as health_router

    monkeypatch.setattr(
        health_router,
        "get_readiness",
        AsyncMock(
            return_value={
                "ready": False,
                "reasons": ["database: error"],
                "database": {"status": "error", "details": {}},
                "migrations": {"alembic_version_present": False, "current": []},
                "task_enqueue": {"available": False, "reason": "db not ready"},
                "version": "test",
                "timestamp": "ts",
            },
        ),
    )
    resp = await client.get("/api/v1/readiness")
    assert resp.status_code == 503
    assert resp.json()["ready"] is False


@pytest.mark.asyncio
async def test_v1_health_reports_seeded_lead_counts(client, db_session, patch_health_session) -> None:
    from tests.factories.lead_factory import create_leads

    await create_leads(db_session, count=3)
    resp = await client.get("/api/v1/health")
    assert resp.status_code in (200, 503)
    body = resp.json()
    assert body["metrics"]["total_leads"] == 3
