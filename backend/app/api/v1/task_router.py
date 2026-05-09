from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.models.task import serialize_task
from app.services.tasks.service import enqueue, get_task
from app.services.tasks.worker import (
    DISPATCH_TABLE,
    _process_one_task_in_own_session,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/enqueue")
async def enqueue_task(
    background_tasks: BackgroundTasks,
    body: dict[str, Any] = Body(...),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    task_type = str(body.get("task_type") or "").strip()
    payload = body.get("payload") or {}
    if not task_type:
        raise HTTPException(status_code=400, detail="task_type is required")
    if task_type not in DISPATCH_TABLE:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unknown task_type '{task_type}'. "
                f"Known: {sorted(DISPATCH_TABLE.keys())}"
            ),
        )
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be a JSON object")

    task = await enqueue(session, task_type, payload)
    background_tasks.add_task(_process_one_task_in_own_session, task.id)
    return {"task_id": str(task.id), "status": task.status}


@router.get("/{task_id}")
async def fetch_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    task = await get_task(session, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return serialize_task(task)
