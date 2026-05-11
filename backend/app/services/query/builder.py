from __future__ import annotations

from typing import Any, Iterable

from sqlalchemy import Select, and_, or_, select
from sqlalchemy.sql import literal_column, text

from app.models.lead import Lead

SORT_FIELD_MAP: dict[str, Any] = {
    "created_at": Lead.created_at,
    "ranking_score": Lead.ranking_score,
    "last_ranked_at": Lead.last_ranked_at,
    "last_routed_at": Lead.last_routed_at,
    "assigned_to": Lead.assigned_to,
    "email": Lead.email,
    "source": Lead.source,
    "id": Lead.id,
}


SEARCHABLE_COLUMNS: tuple[Any, ...] = (
    Lead.email,
    Lead.source,
    Lead.ranking_explanation,
)


def _normalize_term(term: str | None) -> str:
    return (term or "").strip()


def apply_text_search(query: Select[Any], text: str | None) -> Select[Any]:
    term = _normalize_term(text)
    if not term:
        return query
    pattern = f"%{term}%"
    clauses = [col.ilike(pattern) for col in SEARCHABLE_COLUMNS]
    return query.where(or_(*clauses))


def apply_tag_filter(query: Select[Any], tags: Iterable[str] | None) -> Select[Any]:
    if tags is None:
        return query
    cleaned = [t.strip() for t in tags if t and t.strip()]
    if not cleaned:
        return query

    subq: Any = (
        select(literal_column("ltl.lead_id"))
        .select_from(text("lead_tag_link AS ltl JOIN leadtag AS lt ON lt.id = ltl.tag_id"))
        .where(literal_column("lt.name").in_(cleaned))
    )
    return query.where(Lead.id.in_(subq))


def apply_score_range(
    query: Select[Any],
    min_score: float | None,
    max_score: float | None,
) -> Select[Any]:
    conditions: list[Any] = []
    if min_score is not None:
        conditions.append(Lead.ranking_score >= float(min_score))
    if max_score is not None:
        conditions.append(Lead.ranking_score <= float(max_score))
    if not conditions:
        return query
    return query.where(and_(*conditions))


def apply_assignment_filter(query: Select[Any], assigned_to: str | None) -> Select[Any]:
    cleaned = _normalize_term(assigned_to)
    if not cleaned:
        return query
    if not hasattr(Lead, "assigned_to"):
        return query
    return query.where(getattr(Lead, "assigned_to") == cleaned)


def apply_source_filter(query: Select[Any], source: str | None) -> Select[Any]:
    cleaned = _normalize_term(source)
    if not cleaned:
        return query
    return query.where(Lead.source == cleaned)


def apply_sorting(
    query: Select[Any],
    sort_by: str | None,
    sort_dir: str | None,
) -> Select[Any]:
    field_key = (sort_by or "created_at").strip().lower()
    column = SORT_FIELD_MAP.get(field_key, Lead.created_at)
    direction = (sort_dir or "desc").strip().lower()
    if direction not in {"asc", "desc"}:
        direction = "desc"
    ordering = column.asc() if direction == "asc" else column.desc()
    return query.order_by(ordering, Lead.id.asc())


def apply_pagination(query: Select[Any], limit: int, offset: int) -> Select[Any]:
    safe_limit = max(1, min(int(limit), 500))
    safe_offset = max(0, int(offset))
    return query.limit(safe_limit).offset(safe_offset)
