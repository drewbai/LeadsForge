from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai.base import AIProvider
from app.services.ai.semantic_search import semantic_search

logger = logging.getLogger(__name__)


async def _keyword_search(
    session: AsyncSession,
    query: str,
    *,
    limit: int = 50,
) -> list[dict[str, Any]]:
    if not query or not query.strip():
        return []

    pattern = f"%{query.strip()}%"
    sql = text(
        """
        SELECT id AS lead_id, email, source
        FROM leads
        WHERE email ILIKE :p OR source ILIKE :p
        LIMIT :lim
        """
    )
    result = await session.execute(sql, {"p": pattern, "lim": limit})
    rows = result.mappings().all()
    out: list[dict[str, Any]] = []
    for idx, row in enumerate(rows):
        score = 1.0 - (idx / max(len(rows), 1))
        out.append(
            {
                "lead_id": str(row["lead_id"]),
                "email": row["email"],
                "source": row["source"],
                "score": score,
            }
        )
    return out


async def hybrid_search(
    session: AsyncSession,
    provider: AIProvider,
    query: str,
    *,
    limit: int = 10,
    semantic_weight: float = 0.7,
    keyword_weight: float = 0.3,
) -> list[dict[str, Any]]:
    if not query or not query.strip():
        return []

    semantic_results = await semantic_search(
        session, provider, query, limit=max(limit * 4, 20)
    )
    keyword_results = await _keyword_search(
        session, query, limit=max(limit * 4, 20)
    )

    combined: dict[str, dict[str, Any]] = {}
    for item in semantic_results:
        lead_id = item["lead_id"]
        combined[lead_id] = {
            "lead_id": lead_id,
            "email": item.get("email"),
            "source": item.get("source"),
            "semantic_score": float(item.get("score", 0.0)),
            "keyword_score": 0.0,
        }
    for item in keyword_results:
        lead_id = item["lead_id"]
        if lead_id not in combined:
            combined[lead_id] = {
                "lead_id": lead_id,
                "email": item.get("email"),
                "source": item.get("source"),
                "semantic_score": 0.0,
                "keyword_score": float(item.get("score", 0.0)),
            }
        else:
            combined[lead_id]["keyword_score"] = float(item.get("score", 0.0))

    ranked: list[dict[str, Any]] = []
    for entry in combined.values():
        score = (
            semantic_weight * entry["semantic_score"]
            + keyword_weight * entry["keyword_score"]
        )
        entry["score"] = score
        ranked.append(entry)
    ranked.sort(key=lambda r: r["score"], reverse=True)
    return ranked[:limit]
