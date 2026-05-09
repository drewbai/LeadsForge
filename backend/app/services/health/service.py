from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import MetaData, func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import AsyncSessionLocal
from app.version import VERSION

logger = logging.getLogger(__name__)


RECENT_ERROR_WINDOW_HOURS = 24


async def _reflect_metadata(session: AsyncSession) -> MetaData:
    metadata = MetaData()
    await session.run_sync(
        lambda sync_session: metadata.reflect(bind=sync_session.bind)
    )
    return metadata


async def _check_database(session: AsyncSession) -> dict[str, Any]:
    try:
        result = await session.execute(text("SELECT 1"))
        value = result.scalar()
        ok = value == 1
        return {
            "status": "ok" if ok else "degraded",
            "details": {"select_1": value},
        }
    except SQLAlchemyError as exc:
        logger.exception("Database health check failed")
        return {"status": "error", "details": {"error": str(exc)}}


async def _count_table(
    session: AsyncSession,
    metadata: MetaData,
    table_name: str,
    where_clause: Any = None,
) -> int | None:
    table = metadata.tables.get(table_name)
    if table is None:
        return None
    try:
        stmt = select(func.count()).select_from(table)
        if where_clause is not None:
            stmt = stmt.where(where_clause)
        result = await session.execute(stmt)
        return int(result.scalar() or 0)
    except SQLAlchemyError:
        logger.exception("Count failed for table %s", table_name)
        return None


async def _task_stats(
    session: AsyncSession,
    metadata: MetaData,
) -> dict[str, Any]:
    table = metadata.tables.get("task")
    if table is None:
        return {
            "available": False,
            "pending": 0,
            "running": 0,
            "recent_errors": 0,
        }
    pending = await _count_table(
        session, metadata, "task", where_clause=table.c.status == "pending"
    )
    running = await _count_table(
        session, metadata, "task", where_clause=table.c.status == "running"
    )
    cutoff = datetime.now(timezone.utc) - timedelta(hours=RECENT_ERROR_WINDOW_HOURS)
    recent_errors_clause = (table.c.status == "error") & (
        getattr(table.c, "updated_at", table.c.created_at) >= cutoff
    )
    recent_errors = await _count_table(
        session, metadata, "task", where_clause=recent_errors_clause
    )
    return {
        "available": True,
        "pending": pending or 0,
        "running": running or 0,
        "recent_errors": recent_errors or 0,
    }


async def _metric_rollups(
    session: AsyncSession,
    metadata: MetaData,
) -> dict[str, Any]:
    total_leads = await _count_table(session, metadata, "leads")
    total_tasks = await _count_table(session, metadata, "task")
    total_events = await _count_table(session, metadata, "lead_activity_log")
    return {
        "total_leads": total_leads if total_leads is not None else 0,
        "total_tasks": total_tasks if total_tasks is not None else 0,
        "total_events": total_events if total_events is not None else 0,
    }


async def _subscription_stats(
    session: AsyncSession,
    metadata: MetaData,
) -> dict[str, Any]:
    table = metadata.tables.get("subscription")
    if table is None:
        return {"available": False, "active": 0, "by_event_type": {}}
    try:
        active_result = await session.execute(
            select(func.count())
            .select_from(table)
            .where(table.c.is_active.is_(True))
        )
        active = int(active_result.scalar() or 0)

        grouped = await session.execute(
            select(table.c.event_type, func.count())
            .where(table.c.is_active.is_(True))
            .group_by(table.c.event_type)
        )
        by_event_type = {row[0]: int(row[1]) for row in grouped.all()}
    except SQLAlchemyError:
        logger.exception("Subscription stats query failed")
        return {"available": True, "active": 0, "by_event_type": {}}

    return {
        "available": True,
        "active": active,
        "by_event_type": by_event_type,
    }


def _aggregate_status(
    db: dict[str, Any], tasks: dict[str, Any]
) -> str:
    if db.get("status") == "error":
        return "error"
    if tasks.get("recent_errors", 0) > 0 or db.get("status") == "degraded":
        return "degraded"
    return "ok"


async def get_health() -> dict[str, Any]:
    async with AsyncSessionLocal() as session:
        db = await _check_database(session)
        if db["status"] == "error":
            return {
                "status": "error",
                "database": db,
                "tasks": {"pending": 0, "running": 0, "recent_errors": 0},
                "metrics": {"total_leads": 0, "total_tasks": 0, "total_events": 0},
                "subscriptions": {"active": 0, "by_event_type": {}},
                "version": VERSION,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        metadata = await _reflect_metadata(session)
        tasks = await _task_stats(session, metadata)
        metrics = await _metric_rollups(session, metadata)
        subscriptions = await _subscription_stats(session, metadata)

    return {
        "status": _aggregate_status(db, tasks),
        "database": db,
        "tasks": {
            "pending": tasks["pending"],
            "running": tasks["running"],
            "recent_errors": tasks["recent_errors"],
        },
        "metrics": metrics,
        "subscriptions": {
            "active": subscriptions["active"],
            "by_event_type": subscriptions["by_event_type"],
        },
        "version": VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def _check_pending_migrations(session: AsyncSession) -> dict[str, Any]:
    try:
        result = await session.execute(
            text("SELECT version_num FROM alembic_version")
        )
        rows = [row[0] for row in result.all()]
        return {
            "alembic_version_present": True,
            "current": rows,
        }
    except SQLAlchemyError:
        return {
            "alembic_version_present": False,
            "current": [],
        }


async def _check_task_enqueue_capability(
    session: AsyncSession,
    metadata: MetaData,
) -> dict[str, Any]:
    table = metadata.tables.get("task")
    if table is None:
        return {
            "available": False,
            "reason": "task table not present (task engine not migrated)",
        }
    try:
        await session.execute(select(func.count()).select_from(table))
        return {"available": True}
    except SQLAlchemyError as exc:
        return {"available": False, "reason": str(exc)}


async def get_readiness() -> dict[str, Any]:
    reasons: list[str] = []
    async with AsyncSessionLocal() as session:
        db = await _check_database(session)
        if db["status"] != "ok":
            reasons.append(f"database: {db['status']}")
            return {
                "ready": False,
                "reasons": reasons,
                "database": db,
                "migrations": {"alembic_version_present": False, "current": []},
                "task_enqueue": {"available": False, "reason": "db not ready"},
                "version": VERSION,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        metadata = await _reflect_metadata(session)
        migrations = await _check_pending_migrations(session)
        if not migrations["alembic_version_present"]:
            reasons.append("alembic_version table missing")

        task_enqueue = await _check_task_enqueue_capability(session, metadata)
        if not task_enqueue["available"]:
            reasons.append(f"task_enqueue: {task_enqueue.get('reason', 'unavailable')}")

    return {
        "ready": len(reasons) == 0,
        "reasons": reasons,
        "database": db,
        "migrations": migrations,
        "task_enqueue": task_enqueue,
        "version": VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
