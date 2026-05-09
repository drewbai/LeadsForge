from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai.base import AIProvider

logger = logging.getLogger(__name__)


async def semantic_search(
    session: AsyncSession,
    provider: AIProvider,
    query: str,
    *,
    limit: int = 10,
) -> list[dict[str, Any]]:
    if not query or not query.strip():
        return []

    embedding = await provider.generate_embedding(query.strip())
    embedding_literal = "[" + ",".join(repr(float(v)) for v in embedding) + "]"

    sql = text(
        """
        SELECT
            l.id AS lead_id,
            l.email,
            l.source,
            (e.embedding_vector <=> CAST(:emb AS vector)) AS distance
        FROM leads AS l
        JOIN LATERAL (
            SELECT embedding_vector
            FROM lead_ai_embedding
            WHERE lead_id = l.id
            ORDER BY generated_at DESC
            LIMIT 1
        ) AS e ON TRUE
        ORDER BY distance ASC
        LIMIT :lim
        """
    )

    result = await session.execute(sql, {"emb": embedding_literal, "lim": limit})
    rows = result.mappings().all()
    return [
        {
            "lead_id": str(row["lead_id"]),
            "email": row["email"],
            "source": row["source"],
            "distance": float(row["distance"]),
            "score": 1.0 - float(row["distance"]),
        }
        for row in rows
    ]
