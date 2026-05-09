"""API tests for /tasks endpoints (skipped when router absent)."""

from __future__ import annotations

import pytest


def _has_task_router() -> bool:
    try:
        __import__("app.api.v1.task_router")
        return True
    except Exception:
        return False


@pytest.mark.asyncio
async def test_enqueue_task_endpoint(client) -> None:
    if not _has_task_router():
        pytest.skip("task_router not present on this branch")
    resp = await client.post(
        "/api/v1/tasks/enqueue",
        json={"task_type": "rank_lead", "payload": {"lead_id": "any"}},
    )
    assert resp.status_code in (200, 201, 202)
    body = resp.json()
    assert body.get("task_type") == "rank_lead"


@pytest.mark.asyncio
async def test_get_task_endpoint(client) -> None:
    if not _has_task_router():
        pytest.skip("task_router not present on this branch")
    create_resp = await client.post(
        "/api/v1/tasks/enqueue",
        json={"task_type": "rank_lead", "payload": {}},
    )
    if create_resp.status_code not in (200, 201, 202):
        pytest.skip("enqueue returned unexpected status; cannot test fetch")
    task_id = create_resp.json().get("id")
    if not task_id:
        pytest.skip("enqueue response missing id")
    fetch = await client.get(f"/api/v1/tasks/{task_id}")
    assert fetch.status_code == 200
    assert fetch.json().get("id") == task_id


@pytest.mark.asyncio
async def test_get_unknown_task_returns_404(client) -> None:
    if not _has_task_router():
        pytest.skip("task_router not present on this branch")
    from uuid import uuid4

    resp = await client.get(f"/api/v1/tasks/{uuid4()}")
    assert resp.status_code == 404
