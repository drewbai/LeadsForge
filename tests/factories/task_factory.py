"""Factory helpers for Task model instances. Skips when task model not present."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import pytest


def _import_task_model():
    return pytest.importorskip("app.models.task")


def build_task(
    task_type: str = "rank_lead",
    status: str = "pending",
    payload: dict[str, Any] | None = None,
    result: dict[str, Any] | None = None,
    task_id: UUID | None = None,
    created_at: datetime | None = None,
) -> Any:
    module = _import_task_model()
    Task = getattr(module, "Task")
    return Task(
        id=task_id or uuid4(),
        task_type=task_type,
        status=status,
        payload=payload or {},
        result=result,
        created_at=created_at or datetime.now(timezone.utc),
    )


async def create_task(session, **overrides: Any) -> Any:
    task = build_task(**overrides)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
