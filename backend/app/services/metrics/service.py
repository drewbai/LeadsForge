from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metric import Metric, serialize_metric

logger = logging.getLogger(__name__)


def _clean_labels(labels: dict[str, Any] | None) -> dict[str, Any] | None:
    if not labels:
        return None
    cleaned: dict[str, Any] = {}
    for k, v in labels.items():
        if v is None:
            continue
        cleaned[str(k)] = v
    return cleaned or None


async def record(
    session: AsyncSession,
    metric_type: str,
    value: float = 1.0,
    labels: dict[str, Any] | None = None,
) -> Metric:
    cleaned_type = (metric_type or "").strip()
    if not cleaned_type:
        raise ValueError("metric_type is required")
    metric = Metric(
        id=uuid.uuid4(),
        metric_type=cleaned_type,
        value=float(value),
        labels=_clean_labels(labels),
    )
    session.add(metric)
    await session.commit()
    await session.refresh(metric)
    return metric


async def increment(
    session: AsyncSession,
    metric_type: str,
    labels: dict[str, Any] | None = None,
) -> Metric:
    return await record(session, metric_type, 1.0, labels)


async def _run_record(
    metric_type: str,
    value: float,
    labels: dict[str, Any] | None,
) -> None:
    from app.db.engine import AsyncSessionLocal

    try:
        async with AsyncSessionLocal() as session:
            await record(session, metric_type, value, labels)
    except Exception:
        logger.exception(
            "Background metric write failed (type=%s labels=%s)",
            metric_type,
            labels,
        )


async def fire_and_forget_record(
    metric_type: str,
    value: float = 1.0,
    labels: dict[str, Any] | None = None,
) -> None:
    if not metric_type:
        return
    try:
        asyncio.create_task(_run_record(metric_type, float(value), labels))
    except RuntimeError:
        try:
            await _run_record(metric_type, float(value), labels)
        except Exception:
            logger.exception(
                "Inline metric write failed (type=%s labels=%s)",
                metric_type,
                labels,
            )


async def fire_and_forget_increment(
    metric_type: str,
    labels: dict[str, Any] | None = None,
) -> None:
    await fire_and_forget_record(metric_type, 1.0, labels)


async def get_metrics(
    session: AsyncSession,
    *,
    metric_type: str | None = None,
    labels: dict[str, Any] | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    query = select(Metric)
    if metric_type:
        query = query.where(Metric.metric_type == metric_type.strip())
    cleaned_labels = _clean_labels(labels)
    if cleaned_labels:
        query = query.where(Metric.labels.contains(cleaned_labels))

    safe_limit = max(1, min(int(limit), 1000))
    safe_offset = max(0, int(offset))

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = int(total_result.scalar() or 0)

    page_result = await session.execute(
        query.order_by(Metric.created_at.desc(), Metric.id.desc()).limit(safe_limit).offset(safe_offset)
    )
    metrics = [serialize_metric(m) for m in page_result.scalars().all()]

    return {
        "results": metrics,
        "total": total,
        "limit": safe_limit,
        "offset": safe_offset,
        "filters": {
            "metric_type": metric_type,
            "labels": cleaned_labels,
        },
    }
