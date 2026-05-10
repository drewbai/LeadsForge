"""Tests for the health service (Phase 80)."""

from __future__ import annotations

import pytest
from app.services.health import service as health_service


@pytest.mark.asyncio
async def test_get_health_returns_ok_payload(patch_health_session, db_session) -> None:
    payload = await health_service.get_health()

    assert payload["status"] in {"ok", "degraded"}
    assert payload["database"]["status"] == "ok"
    assert "version" in payload
    assert "timestamp" in payload
    assert payload["metrics"]["total_leads"] >= 0
    assert "subscriptions" in payload
    assert "tasks" in payload


@pytest.mark.asyncio
async def test_get_health_counts_seeded_leads(patch_health_session, db_session) -> None:
    from tests.factories.lead_factory import create_leads

    await create_leads(db_session, count=4)
    payload = await health_service.get_health()
    assert payload["metrics"]["total_leads"] == 4


@pytest.mark.asyncio
async def test_get_readiness_reports_status(patch_health_session, db_session) -> None:
    payload = await health_service.get_readiness()
    assert "ready" in payload
    assert "reasons" in payload
    assert "database" in payload
    assert "migrations" in payload
    assert "task_enqueue" in payload
    assert "version" in payload


@pytest.mark.asyncio
async def test_get_readiness_not_ready_without_alembic(patch_health_session, db_session) -> None:
    payload = await health_service.get_readiness()
    assert payload["ready"] is False
    assert any("alembic" in r.lower() for r in payload["reasons"])


@pytest.mark.asyncio
async def test_get_health_degraded_when_recent_task_errors(
    patch_health_session,
    db_session,
    monkeypatch,
) -> None:
    async def _fake_task_stats(_session, _metadata):
        return {
            "available": True,
            "pending": 0,
            "running": 0,
            "recent_errors": 2,
        }

    monkeypatch.setattr(health_service, "_task_stats", _fake_task_stats)
    payload = await health_service.get_health()
    assert payload["status"] == "degraded"


@pytest.mark.asyncio
async def test_get_health_error_branch_when_db_unreachable(patch_health_session, db_session, monkeypatch) -> None:
    async def _bad_db(_session):
        return {"status": "error", "details": {"error": "connection refused"}}

    monkeypatch.setattr(health_service, "_check_database", _bad_db)
    payload = await health_service.get_health()
    assert payload["status"] == "error"
    assert payload["database"]["status"] == "error"
    assert payload["metrics"] == {"total_leads": 0, "total_tasks": 0, "total_events": 0}
    assert payload["subscriptions"] == {"active": 0, "by_event_type": {}}


@pytest.mark.asyncio
async def test_get_health_handles_session_factory_failure(monkeypatch) -> None:
    class _Boom:
        async def __aenter__(self):
            raise RuntimeError("db down")

        async def __aexit__(self, *args):
            return False

    def _factory():
        return _Boom()

    monkeypatch.setattr(health_service, "AsyncSessionLocal", _factory)
    with pytest.raises(RuntimeError):
        await health_service.get_health()
