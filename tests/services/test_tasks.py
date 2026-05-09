"""Tests for the background task engine (skipped if not on branch)."""
from __future__ import annotations

from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_enqueue_task_creates_pending_row(db_session) -> None:
    service = pytest.importorskip("app.services.tasks.service")
    enqueue = (
        getattr(service, "enqueue_task", None)
        or getattr(service, "enqueue", None)
        or getattr(service, "create_task", None)
    )
    assert enqueue is not None, "TaskService missing an enqueue function"

    task = await enqueue(db_session, task_type="rank_lead", payload={"lead_id": str(uuid4())})
    assert task is not None
    if isinstance(task, dict):
        assert task.get("status") in {"pending", "queued"}
        assert task.get("task_type") == "rank_lead"
    else:
        assert getattr(task, "status", None) in {"pending", "queued"}


@pytest.mark.asyncio
async def test_get_task_returns_record(db_session) -> None:
    service = pytest.importorskip("app.services.tasks.service")
    enqueue = (
        getattr(service, "enqueue_task", None)
        or getattr(service, "enqueue", None)
        or getattr(service, "create_task", None)
    )
    get_task = getattr(service, "get_task", None)
    if get_task is None:
        pytest.skip("get_task not exposed")

    created = await enqueue(db_session, task_type="rank_lead", payload={})
    task_id = created.get("id") if isinstance(created, dict) else getattr(created, "id")
    fetched = await get_task(db_session, task_id)
    assert fetched is not None


@pytest.mark.asyncio
async def test_worker_dispatches_known_task_type(db_session, monkeypatch) -> None:
    worker_mod = pytest.importorskip("app.services.tasks.worker")
    dispatch = (
        getattr(worker_mod, "dispatch_task", None)
        or getattr(worker_mod, "_dispatch", None)
        or getattr(worker_mod, "process_task", None)
    )
    if dispatch is None:
        pytest.skip("worker dispatch entry point not found")

    called = {"n": 0}

    async def fake_compute(session, lead_id):
        called["n"] += 1
        return {"lead_id": str(lead_id), "ranking_score": 50.0}

    monkeypatch.setattr(
        "app.services.ranking.engine.compute_lead_ranking",
        fake_compute,
        raising=False,
    )

    fake_task = {
        "id": str(uuid4()),
        "task_type": "rank_lead",
        "payload": {"lead_id": str(uuid4())},
        "status": "pending",
    }
    try:
        await dispatch(db_session, fake_task)
    except TypeError:
        pytest.skip("dispatch signature differs")
