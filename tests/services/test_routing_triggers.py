"""Tests for app.services.routing.triggers.enqueue_routing_recompute.

Phase 74 routing trigger should:
- Persist a ``route_lead`` task via the canonical Phase 77 task engine.
- Be a no-op for ``lead_id is None``.
- Swallow all exceptions (best-effort side-effect of the primary write).

Mirrors tests/services/test_ranking_triggers.py exactly so any regression in
the trigger contract on either side fails loudly in symmetric form.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from app.models.task import TASK_STATUS_PENDING, Task
from app.services.routing import triggers as routing_triggers
from app.services.routing.triggers import ROUTING_TASK_TYPE, enqueue_routing_recompute
from sqlalchemy import select


@pytest.mark.asyncio
async def test_enqueue_routing_recompute_persists_route_lead_task(db_session, session_factory, monkeypatch) -> None:
    monkeypatch.setattr("app.db.engine.AsyncSessionLocal", session_factory, raising=False)

    lead_id = uuid4()
    await enqueue_routing_recompute(lead_id)

    rows = (await db_session.execute(select(Task))).scalars().all()
    assert len(rows) == 1
    task = rows[0]
    assert task.task_type == ROUTING_TASK_TYPE
    assert task.status == TASK_STATUS_PENDING
    assert task.payload == {"lead_id": str(lead_id)}


@pytest.mark.asyncio
async def test_enqueue_routing_recompute_noop_for_none_lead_id(db_session, session_factory, monkeypatch) -> None:
    monkeypatch.setattr("app.db.engine.AsyncSessionLocal", session_factory, raising=False)

    await enqueue_routing_recompute(None)

    rows = (await db_session.execute(select(Task))).scalars().all()
    assert rows == []


@pytest.mark.asyncio
async def test_enqueue_routing_recompute_swallows_failures(monkeypatch, caplog) -> None:
    class _BoomSession:
        async def __aenter__(self):
            raise RuntimeError("db down")

        async def __aexit__(self, *exc_info):
            return False

    monkeypatch.setattr("app.db.engine.AsyncSessionLocal", lambda: _BoomSession(), raising=False)

    with caplog.at_level("ERROR", logger=routing_triggers.__name__):
        await enqueue_routing_recompute(uuid4())

    assert any("Failed to enqueue route_lead task" in record.getMessage() for record in caplog.records)


def test_routing_task_type_constant_matches_dispatch_table() -> None:
    """Guard: ``ROUTING_TASK_TYPE`` must match a key in the worker dispatch table.

    If the worker renames the ``route_lead`` handler, this test fails loudly so
    the trigger gets updated in the same change.
    """
    from app.services.tasks.worker import DISPATCH_TABLE

    assert ROUTING_TASK_TYPE in DISPATCH_TABLE
