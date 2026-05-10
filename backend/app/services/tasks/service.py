from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import (
    TASK_STATUS_ERROR,
    TASK_STATUS_PENDING,
    TASK_STATUS_RUNNING,
    TASK_STATUS_SUCCESS,
    Task,
)

logger = logging.getLogger(__name__)


async def enqueue(
    session: AsyncSession,
    task_type: str,
    payload: dict[str, Any] | None = None,
) -> Task:
    cleaned_type = (task_type or "").strip()
    if not cleaned_type:
        raise ValueError("task_type is required")
    task = Task(
        id=uuid.uuid4(),
        task_type=cleaned_type,
        status=TASK_STATUS_PENDING,
        payload=dict(payload or {}),
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_task(session: AsyncSession, task_id: uuid.UUID) -> Task | None:
    result = await session.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def mark_running(session: AsyncSession, task_id: uuid.UUID) -> Task | None:
    now = datetime.now(timezone.utc)
    await session.execute(
        update(Task).where(Task.id == task_id).values(status=TASK_STATUS_RUNNING, started_at=now, updated_at=now)
    )
    await session.commit()
    return await get_task(session, task_id)


async def mark_success(
    session: AsyncSession,
    task_id: uuid.UUID,
    result: dict[str, Any] | None,
) -> Task | None:
    now = datetime.now(timezone.utc)
    await session.execute(
        update(Task)
        .where(Task.id == task_id)
        .values(
            status=TASK_STATUS_SUCCESS,
            result=dict(result) if result is not None else None,
            error_message=None,
            finished_at=now,
            updated_at=now,
        )
    )
    await session.commit()
    return await get_task(session, task_id)


async def mark_error(
    session: AsyncSession,
    task_id: uuid.UUID,
    error: str,
) -> Task | None:
    now = datetime.now(timezone.utc)
    await session.execute(
        update(Task)
        .where(Task.id == task_id)
        .values(
            status=TASK_STATUS_ERROR,
            error_message=str(error)[:8000],
            finished_at=now,
            updated_at=now,
        )
    )
    await session.commit()
    return await get_task(session, task_id)


async def claim_pending_tasks(
    session: AsyncSession,
    *,
    limit: int = 10,
) -> list[Task]:
    result = await session.execute(
        select(Task)
        .where(Task.status == TASK_STATUS_PENDING)
        .order_by(Task.created_at.asc(), Task.id.asc())
        .limit(int(limit))
    )
    return list(result.scalars().all())
