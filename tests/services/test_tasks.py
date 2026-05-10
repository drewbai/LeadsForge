"""Deterministic tests for the Phase 77 background task engine.

Grounded in app/services/tasks/{service.py,worker.py} and app/models/task.py.
Skips entire file if the `task` table or service module is absent on the
current branch (so dev keeps passing until Phase 77 merges).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

import pytest
import pytest_asyncio

pytestmark = pytest.mark.asyncio


def _require_task_engine():
    pytest.importorskip("app.models.task")
    return (
        pytest.importorskip("app.services.tasks.service"),
        pytest.importorskip("app.services.tasks.worker"),
    )


@pytest_asyncio.fixture
async def task_engine():
    return _require_task_engine()


async def test_enqueue_creates_pending_row(db_session, task_engine) -> None:
    service, _worker = task_engine
    task = await service.enqueue(
        db_session,
        task_type="rank_lead",
        payload={"lead_id": str(uuid4())},
    )
    assert isinstance(task.id, UUID)
    assert task.task_type == "rank_lead"
    assert task.status == "pending"
    assert task.payload["lead_id"]
    assert task.result is None
    assert task.started_at is None
    assert task.finished_at is None


async def test_enqueue_rejects_blank_task_type(db_session, task_engine) -> None:
    service, _ = task_engine
    with pytest.raises(ValueError):
        await service.enqueue(db_session, task_type="   ", payload={})


async def test_get_task_returns_record(db_session, task_engine) -> None:
    service, _ = task_engine
    created = await service.enqueue(db_session, task_type="rank_lead", payload={})
    fetched = await service.get_task(db_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id


async def test_get_task_returns_none_when_missing(db_session, task_engine) -> None:
    service, _ = task_engine
    assert await service.get_task(db_session, uuid4()) is None


async def test_mark_running_then_success_records_lifecycle(db_session, task_engine) -> None:
    service, _ = task_engine
    created = await service.enqueue(db_session, task_type="rank_lead", payload={})
    running = await service.mark_running(db_session, created.id)
    assert running is not None
    assert running.status == "running"
    assert running.started_at is not None

    finished = await service.mark_success(db_session, created.id, {"score": 1.0})
    assert finished is not None
    assert finished.status == "success"
    assert finished.result == {"score": 1.0}
    assert finished.error_message is None
    assert finished.finished_at is not None


async def test_mark_error_records_failure(db_session, task_engine) -> None:
    service, _ = task_engine
    created = await service.enqueue(db_session, task_type="rank_lead", payload={})
    errored = await service.mark_error(db_session, created.id, "boom")
    assert errored is not None
    assert errored.status == "error"
    assert errored.error_message == "boom"
    assert errored.finished_at is not None


async def test_claim_pending_tasks_returns_in_creation_order(db_session, task_engine) -> None:
    service, _ = task_engine
    a = await service.enqueue(db_session, task_type="rank_lead", payload={"n": 1})
    b = await service.enqueue(db_session, task_type="rank_lead", payload={"n": 2})
    pending = await service.claim_pending_tasks(db_session, limit=10)
    assert [t.id for t in pending] == [a.id, b.id]


async def test_dispatch_table_excludes_route_lead_until_phase_74(task_engine) -> None:
    _, worker = task_engine
    assert "route_lead" not in worker.DISPATCH_TABLE, (
        "route_lead handler must stay out of DISPATCH_TABLE until Phase 74 lands"
    )
    expected = {"enrich_lead", "rank_lead", "ai_summary", "ai_insight", "ai_embedding"}
    assert expected.issubset(set(worker.DISPATCH_TABLE.keys()))


async def test_execute_task_happy_path_calls_handler_and_marks_success(db_session, task_engine) -> None:
    service, worker = task_engine
    lead_id = uuid4()

    async def fake_compute(session, _lead_id):
        return {
            "lead_id": str(_lead_id),
            "ranking_score": 87.5,
            "ranking_explanation": "test",
        }

    with patch(
        "app.services.ranking.engine.compute_lead_ranking",
        new=AsyncMock(side_effect=fake_compute),
    ):
        task = await service.enqueue(db_session, task_type="rank_lead", payload={"lead_id": str(lead_id)})
        outcome = await worker.execute_task(db_session, task)

    assert outcome["status"] == "success"
    assert outcome["task_id"] == str(task.id)
    refreshed = await service.get_task(db_session, task.id)
    assert refreshed is not None
    assert refreshed.status == "success"
    assert refreshed.result is not None
    assert refreshed.result["ranking"]["ranking_score"] == 87.5


async def test_execute_task_unknown_type_marks_error(db_session, task_engine) -> None:
    service, worker = task_engine
    task = await service.enqueue(db_session, task_type="rank_lead", payload={})
    task.task_type = "definitely-not-registered"  # type: ignore[assignment]
    outcome = await worker.execute_task(db_session, task)
    assert outcome["status"] == "error"
    assert "Unknown task_type" in outcome["error"]


async def test_execute_task_handler_exception_marks_error(db_session, task_engine) -> None:
    service, worker = task_engine

    async def boom(session, _lead_id):
        raise RuntimeError("handler failed on purpose")

    with patch(
        "app.services.ranking.engine.compute_lead_ranking",
        new=AsyncMock(side_effect=boom),
    ):
        task = await service.enqueue(
            db_session,
            task_type="rank_lead",
            payload={"lead_id": str(uuid4())},
        )
        outcome = await worker.execute_task(db_session, task)

    assert outcome["status"] == "error"
    assert "handler failed on purpose" in outcome["error"]
    refreshed = await service.get_task(db_session, task.id)
    assert refreshed is not None
    assert refreshed.status == "error"
    assert refreshed.error_message is not None
    assert "handler failed on purpose" in refreshed.error_message
