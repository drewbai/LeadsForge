"""Tests for the health service."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_get_health_returns_ok_payload(patch_health_session, db_session) -> None:
    health = pytest.importorskip("app.services.health.service")

    payload = await health.get_health()

    assert payload["status"] in {"ok", "degraded"}
    assert payload["database"]["status"] == "ok"
    assert "version" in payload
    assert "timestamp" in payload
    assert payload["metrics"]["total_leads"] >= 0
    assert "subscriptions" in payload
    assert "tasks" in payload


@pytest.mark.asyncio
async def test_get_health_counts_seeded_leads(patch_health_session, db_session) -> None:
    health = pytest.importorskip("app.services.health.service")
    from tests.factories.lead_factory import create_leads

    await create_leads(db_session, count=4)
    payload = await health.get_health()
    assert payload["metrics"]["total_leads"] == 4


@pytest.mark.asyncio
async def test_get_readiness_reports_status(patch_health_session, db_session) -> None:
    health = pytest.importorskip("app.services.health.service")

    payload = await health.get_readiness()
    assert "ready" in payload
    assert "reasons" in payload
    assert "database" in payload
    assert "version" in payload


@pytest.mark.asyncio
async def test_get_health_handles_database_error(monkeypatch) -> None:
    health = pytest.importorskip("app.services.health.service")

    class _Boom:
        async def __aenter__(self):
            raise RuntimeError("db down")

        async def __aexit__(self, *args):
            return False

    def _factory():
        return _Boom()

    monkeypatch.setattr(health, "AsyncSessionLocal", _factory)
    with pytest.raises(RuntimeError):
        await health.get_health()
