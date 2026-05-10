from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any, Awaitable, Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead, serialize_lead
from app.models.task import Task
from app.services.tasks.service import (
    claim_pending_tasks,
    mark_error,
    mark_running,
    mark_success,
)

logger = logging.getLogger(__name__)


TaskHandler = Callable[[AsyncSession, dict[str, Any]], Awaitable[dict[str, Any]]]


def _payload_lead_id(payload: dict[str, Any]) -> uuid.UUID:
    raw = payload.get("lead_id")
    if raw is None:
        raise ValueError("payload.lead_id is required")
    if isinstance(raw, uuid.UUID):
        return raw
    return uuid.UUID(str(raw))


async def _load_lead(session: AsyncSession, lead_id: uuid.UUID) -> Lead | None:
    result = await session.execute(select(Lead).where(Lead.id == lead_id))
    return result.scalar_one_or_none()


async def _handle_enrich_lead(
    session: AsyncSession, payload: dict[str, Any]
) -> dict[str, Any]:
    from app.services.enrichment_service import enrich_lead

    lead_id = _payload_lead_id(payload)
    lead = await _load_lead(session, lead_id)
    if lead is None:
        return {"status": "skipped", "reason": "lead not found", "lead_id": str(lead_id)}
    enriched = await enrich_lead(serialize_lead(lead), lead_id=lead_id)
    return {"status": "ok", "lead_id": str(lead_id), "enriched": enriched}


async def _handle_rank_lead(
    session: AsyncSession, payload: dict[str, Any]
) -> dict[str, Any]:
    from app.services.ranking.engine import compute_lead_ranking

    lead_id = _payload_lead_id(payload)
    result = await compute_lead_ranking(session, lead_id)
    if result is None:
        return {"status": "skipped", "reason": "lead not found", "lead_id": str(lead_id)}
    return {"status": "ok", "ranking": result}


def _resolve_ai_provider():
    from app.services.ai.openai_provider import OpenAIProvider

    return OpenAIProvider()


async def _handle_ai_summary(
    session: AsyncSession, payload: dict[str, Any]
) -> dict[str, Any]:
    from app.services.ai.summary_pipeline import generate_summary_for_lead

    lead_id = _payload_lead_id(payload)
    provider = _resolve_ai_provider()
    result = await generate_summary_for_lead(session, provider, lead_id)
    if result is None:
        return {"status": "skipped", "reason": "lead not found", "lead_id": str(lead_id)}
    return {"status": "ok", "summary": result}


async def _handle_ai_insight(
    session: AsyncSession, payload: dict[str, Any]
) -> dict[str, Any]:
    from app.services.ai.insight_pipeline import generate_insights_for_lead

    lead_id = _payload_lead_id(payload)
    provider = _resolve_ai_provider()
    result = await generate_insights_for_lead(session, provider, lead_id)
    if result is None:
        return {"status": "skipped", "reason": "lead not found", "lead_id": str(lead_id)}
    return {"status": "ok", "insights": result, "count": len(result)}


async def _handle_ai_embedding(
    session: AsyncSession, payload: dict[str, Any]
) -> dict[str, Any]:
    from app.services.ai.embedding_pipeline import generate_embedding_for_lead

    lead_id = _payload_lead_id(payload)
    provider = _resolve_ai_provider()
    result = await generate_embedding_for_lead(session, provider, lead_id)
    if result is None:
        return {"status": "skipped", "reason": "lead not found", "lead_id": str(lead_id)}
    return {"status": "ok", "embedding": result}


DISPATCH_TABLE: dict[str, TaskHandler] = {
    # NOTE: "route_lead" handler is intentionally absent on dev because
    # app.services.routing.engine is not yet merged (Phase 74). It will be
    # re-added in the Phase 74 PR. Until then, POST /api/v1/tasks/enqueue
    # with task_type="route_lead" returns HTTP 400 "Unknown task_type".
    "enrich_lead": _handle_enrich_lead,
    "rank_lead": _handle_rank_lead,
    "ai_summary": _handle_ai_summary,
    "ai_insight": _handle_ai_insight,
    "ai_embedding": _handle_ai_embedding,
}


async def execute_task(session: AsyncSession, task: Task) -> dict[str, Any]:
    handler = DISPATCH_TABLE.get(task.task_type)
    if handler is None:
        message = f"Unknown task_type: {task.task_type}"
        logger.error(message)
        await mark_error(session, task.id, message)
        return {"status": "error", "task_id": str(task.id), "error": message}

    await mark_running(session, task.id)
    try:
        result = await handler(session, dict(task.payload or {}))
    except Exception as exc:
        logger.exception("Task %s (%s) failed", task.id, task.task_type)
        await mark_error(session, task.id, repr(exc))
        return {"status": "error", "task_id": str(task.id), "error": repr(exc)}

    await mark_success(session, task.id, result)
    return {"status": "success", "task_id": str(task.id), "result": result}


async def process_pending_tasks(
    session: AsyncSession,
    *,
    batch_size: int = 10,
) -> list[dict[str, Any]]:
    pending = await claim_pending_tasks(session, limit=batch_size)
    outcomes: list[dict[str, Any]] = []
    for task in pending:
        outcomes.append(await execute_task(session, task))
    return outcomes


async def _process_one_task_in_own_session(task_id: uuid.UUID) -> None:
    from app.db.engine import AsyncSessionLocal
    from app.services.tasks.service import get_task

    try:
        async with AsyncSessionLocal() as session:
            task = await get_task(session, task_id)
            if task is None:
                logger.warning("Task %s not found for processing", task_id)
                return
            await execute_task(session, task)
    except Exception:
        logger.exception("Failed to process task %s", task_id)


async def run_worker_loop(
    *,
    poll_interval_seconds: float = 2.0,
    batch_size: int = 10,
    stop_event: asyncio.Event | None = None,
) -> None:
    from app.db.engine import AsyncSessionLocal

    while True:
        if stop_event is not None and stop_event.is_set():
            return
        try:
            async with AsyncSessionLocal() as session:
                await process_pending_tasks(session, batch_size=batch_size)
        except Exception:
            logger.exception("Worker loop iteration failed")
        await asyncio.sleep(max(0.1, float(poll_interval_seconds)))
