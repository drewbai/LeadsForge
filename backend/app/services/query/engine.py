from __future__ import annotations

import logging
from typing import Any, Iterable

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead, serialize_lead
from app.services.query.builder import (
    apply_assignment_filter,
    apply_pagination,
    apply_score_range,
    apply_sorting,
    apply_source_filter,
    apply_tag_filter,
    apply_text_search,
)

logger = logging.getLogger(__name__)


def _build_filtered_query(
    *,
    text: str | None,
    tags: Iterable[str] | None,
    min_score: float | None,
    max_score: float | None,
    assigned_to: str | None,
    source: str | None,
):
    query = select(Lead)
    query = apply_text_search(query, text)
    query = apply_tag_filter(query, tags)
    query = apply_score_range(query, min_score, max_score)
    query = apply_assignment_filter(query, assigned_to)
    query = apply_source_filter(query, source)
    return query


async def search_leads(
    session: AsyncSession,
    *,
    text: str | None = None,
    tags: Iterable[str] | None = None,
    min_score: float | None = None,
    max_score: float | None = None,
    assigned_to: str | None = None,
    source: str | None = None,
    sort_by: str | None = "created_at",
    sort_dir: str | None = "desc",
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    base_query = _build_filtered_query(
        text=text,
        tags=tags,
        min_score=min_score,
        max_score=max_score,
        assigned_to=assigned_to,
        source=source,
    )

    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await session.execute(count_query)
    total = int(total_result.scalar() or 0)

    sorted_query = apply_sorting(base_query, sort_by, sort_dir)
    paginated_query = apply_pagination(sorted_query, limit, offset)

    page_result = await session.execute(paginated_query)
    leads = list(page_result.scalars().all())

    return {
        "results": [serialize_lead(lead) for lead in leads],
        "total": total,
        "limit": int(limit),
        "offset": int(offset),
        "filters": {
            "text": text,
            "tags": list(tags) if tags is not None else None,
            "min_score": min_score,
            "max_score": max_score,
            "assigned_to": assigned_to,
            "source": source,
        },
        "sort": {
            "sort_by": sort_by,
            "sort_dir": sort_dir,
        },
    }
