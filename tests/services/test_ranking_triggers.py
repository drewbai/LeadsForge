"""Tests for app.services.ranking.triggers.enqueue_ranking_recompute.

Phase 73 ranking trigger should:
- Persist a ``rank_lead`` task via the canonical Phase 77 task engine.
- Be a no-op for ``lead_id is None``.
- Swallow all exceptions (best-effort side-effect of the primary write).
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from app.models.task import TASK_STATUS_PENDING, Task
from app.services.ranking import triggers as ranking_triggers
from app.services.ranking.triggers import RANKING_TASK_TYPE, enqueue_ranking_recompute
from sqlalchemy import select


@pytest.mark.asyncio
async def test_enqueue_ranking_recompute_persists_rank_lead_task(
    db_session, session_factory, monkeypatch
) -> None:
    monkeypatch.setattr(
        "app.db.engine.AsyncSessionLocal", session_factory, raising=False
    )

    lead_id = uuid4()
    await enqueue_ranking_recompute(lead_id)

    rows = (await db_session.execute(select(Task))).scalars().all()
    assert len(rows) == 1
    task = rows[0]
    assert task.task_type == RANKING_TASK_TYPE
    assert task.status == TASK_STATUS_PENDING
    assert task.payload == {"lead_id": str(lead_id)}


@pytest.mark.asyncio
async def test_enqueue_ranking_recompute_noop_for_none_lead_id(
    db_session, session_factory, monkeypatch
) -> None:
    monkeypatch.setattr(
        "app.db.engine.AsyncSessionLocal", session_factory, raising=False
    )

    await enqueue_ranking_recompute(None)

    rows = (await db_session.execute(select(Task))).scalars().all()
    assert rows == []


@pytest.mark.asyncio
async def test_enqueue_ranking_recompute_swallows_failures(monkeypatch, caplog) -> None:
    class _BoomSession:
        async def __aenter__(self):
            raise RuntimeError("db down")

        async def __aexit__(self, *exc_info):
            return False

    monkeypatch.setattr(
        "app.db.engine.AsyncSessionLocal", lambda: _BoomSession(), raising=False
    )

    with caplog.at_level("ERROR", logger=ranking_triggers.__name__):
        await enqueue_ranking_recompute(uuid4())

    assert any(
        "Failed to enqueue rank_lead task" in record.getMessage()
        for record in caplog.records
    )


def test_ranking_task_type_constant_matches_dispatch_table() -> None:
    """Guard: ``RANKING_TASK_TYPE`` must match a key in the worker dispatch table.

    If the worker renames the ``rank_lead`` handler, this test fails loudly so the
    trigger gets updated in the same change.
    """
    from app.services.tasks.worker import DISPATCH_TABLE

    assert RANKING_TASK_TYPE in DISPATCH_TABLE
