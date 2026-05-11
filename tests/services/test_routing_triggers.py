"""Tests for routing task enqueue (Phase 82)."""

from __future__ import annotations

import pytest
from app.models.task import Task
from app.services.routing import triggers as routing_triggers
from sqlalchemy import select


@pytest.mark.asyncio
async def test_enqueue_route_lead_creates_pending_task(
    db_session,
    seeded_lead,
    session_factory,
    monkeypatch,
) -> None:
    monkeypatch.setattr("app.db.engine.AsyncSessionLocal", session_factory)
    await routing_triggers.enqueue_route_lead(seeded_lead.id)
    result = await db_session.execute(select(Task))
    rows = result.scalars().all()
    assert len(rows) == 1
    assert rows[0].task_type == routing_triggers.ROUTING_TASK_TYPE
    assert rows[0].status == "pending"


@pytest.mark.asyncio
async def test_enqueue_route_lead_no_op_for_none(monkeypatch, session_factory) -> None:
    monkeypatch.setattr("app.db.engine.AsyncSessionLocal", session_factory)
    await routing_triggers.enqueue_route_lead(None)
