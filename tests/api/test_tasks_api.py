"""Deterministic API tests for /api/v1/tasks endpoints (Phase 77).

Skips when task_router is not installed on the current branch.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

pytestmark = pytest.mark.asyncio


def _has_task_router() -> bool:
    try:
        __import__("app.api.v1.task_router")
        return True
    except Exception:
        return False


def _skip_if_no_router() -> None:
    if not _has_task_router():
        pytest.skip("task_router not present on this branch")


async def test_enqueue_endpoint_creates_task_and_returns_id(client) -> None:
    _skip_if_no_router()

    async def fake_compute(session, lead_id):
        return {"lead_id": str(lead_id), "ranking_score": 50.0}

    with patch(
        "app.services.ranking.engine.compute_lead_ranking",
        new=AsyncMock(side_effect=fake_compute),
    ):
        resp = await client.post(
            "/api/v1/tasks/enqueue",
            json={"task_type": "rank_lead", "payload": {"lead_id": str(uuid4())}},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert "task_id" in body
    assert body["status"] == "pending"


async def test_enqueue_endpoint_rejects_unknown_task_type(client) -> None:
    _skip_if_no_router()
    resp = await client.post(
        "/api/v1/tasks/enqueue",
        json={"task_type": "totally_made_up", "payload": {}},
    )
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert "Unknown task_type" in detail


async def test_enqueue_endpoint_accepts_route_lead(client) -> None:
    _skip_if_no_router()

    async def fake_route(session, lead_id):
        return {"lead_id": str(lead_id), "assigned_to": "queue:default", "reason": "fallback"}

    with patch(
        "app.services.routing.engine.route_lead",
        new=AsyncMock(side_effect=fake_route),
    ):
        resp = await client.post(
            "/api/v1/tasks/enqueue",
            json={"task_type": "route_lead", "payload": {"lead_id": str(uuid4())}},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert "task_id" in body
    assert body["status"] == "pending"


async def test_enqueue_endpoint_rejects_missing_task_type(client) -> None:
    _skip_if_no_router()
    resp = await client.post("/api/v1/tasks/enqueue", json={"payload": {}})
    assert resp.status_code == 400


async def test_enqueue_endpoint_rejects_non_object_payload(client) -> None:
    _skip_if_no_router()
    resp = await client.post(
        "/api/v1/tasks/enqueue",
        json={"task_type": "rank_lead", "payload": "not-an-object"},
    )
    assert resp.status_code == 400


async def test_get_task_endpoint_returns_serialized_task(client, db_session) -> None:
    _skip_if_no_router()
    service = pytest.importorskip("app.services.tasks.service")
    created = await service.enqueue(db_session, task_type="rank_lead", payload={"lead_id": str(uuid4())})
    resp = await client.get(f"/api/v1/tasks/{created.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == str(created.id)
    assert body["task_type"] == "rank_lead"
    assert body["status"] in {"pending", "running", "success", "error"}
    assert "payload" in body
    assert "created_at" in body


async def test_get_unknown_task_returns_404(client) -> None:
    _skip_if_no_router()
    resp = await client.get(f"/api/v1/tasks/{uuid4()}")
    assert resp.status_code == 404
