"""Deterministic API tests for /api/v1/tasks endpoints (Phase 77 + Phase 81)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from app.services.tasks import service as task_service

pytestmark = pytest.mark.asyncio


async def test_enqueue_endpoint_creates_task_and_returns_id(client) -> None:
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
    resp = await client.post(
        "/api/v1/tasks/enqueue",
        json={"task_type": "totally_made_up", "payload": {}},
    )
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert "Unknown task_type" in detail


async def test_enqueue_endpoint_accepts_route_lead(client, db_session, seeded_lead) -> None:
    seeded_lead.ranking_score = 82.0
    db_session.add(seeded_lead)
    await db_session.commit()

    resp = await client.post(
        "/api/v1/tasks/enqueue",
        json={"task_type": "route_lead", "payload": {"lead_id": str(seeded_lead.id)}},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "task_id" in body
    assert body["status"] == "pending"


async def test_enqueue_endpoint_rejects_missing_task_type(client) -> None:
    resp = await client.post("/api/v1/tasks/enqueue", json={"payload": {}})
    assert resp.status_code == 400


async def test_enqueue_endpoint_rejects_non_object_payload(client) -> None:
    resp = await client.post(
        "/api/v1/tasks/enqueue",
        json={"task_type": "rank_lead", "payload": "not-an-object"},
    )
    assert resp.status_code == 400


async def test_get_task_endpoint_returns_serialized_task(client, db_session) -> None:
    created = await task_service.enqueue(
        db_session,
        task_type="rank_lead",
        payload={"lead_id": str(uuid4())},
    )
    resp = await client.get(f"/api/v1/tasks/{created.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == str(created.id)
    assert body["task_type"] == "rank_lead"
    assert body["status"] in {"pending", "running", "success", "error"}
    assert "payload" in body
    assert "created_at" in body


async def test_get_unknown_task_returns_404(client) -> None:
    resp = await client.get(f"/api/v1/tasks/{uuid4()}")
    assert resp.status_code == 404
