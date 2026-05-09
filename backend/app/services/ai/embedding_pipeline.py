from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import MetaData, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai.base import AIProvider

logger = logging.getLogger(__name__)


def _build_embedding_text(
    lead: dict[str, Any],
    summary: dict[str, Any] | None,
    insights: list[dict[str, Any]],
) -> str:
    parts: list[str] = []
    for key in ("full_name", "email", "phone", "source", "status", "notes"):
        value = lead.get(key)
        if value:
            parts.append(f"{key}: {value}")
    if summary and summary.get("summary_text"):
        parts.append("summary: " + str(summary["summary_text"]))
    for ins in insights:
        ins_type = ins.get("insight_type")
        ins_text = ins.get("insight_text")
        if ins_type and ins_text:
            parts.append(f"{ins_type}: {ins_text}")
    if not parts:
        parts.append(f"lead {lead.get('id')}")
    return "\n".join(parts)


async def generate_embedding_for_lead(
    session: AsyncSession,
    provider: AIProvider,
    lead_id: uuid.UUID,
    *,
    model_name: str | None = None,
) -> dict[str, Any] | None:
    metadata = MetaData()
    await session.run_sync(lambda sync_session: metadata.reflect(bind=sync_session.bind))
    leads = metadata.tables.get("leads")
    summary_table = metadata.tables.get("lead_ai_summary")
    insight_table = metadata.tables.get("lead_ai_insight")
    embedding_table = metadata.tables.get("lead_ai_embedding")
    if leads is None or embedding_table is None:
        raise RuntimeError("Required tables (leads, lead_ai_embedding) not found")

    lead_result = await session.execute(select(leads).where(leads.c.id == lead_id))
    lead_data = lead_result.mappings().first()
    if lead_data is None:
        return None

    summary_data: dict[str, Any] | None = None
    if summary_table is not None:
        summary_result = await session.execute(
            select(summary_table)
            .where(summary_table.c.lead_id == lead_id)
            .order_by(summary_table.c.generated_at.desc())
            .limit(1)
        )
        summary_row = summary_result.mappings().first()
        summary_data = dict(summary_row) if summary_row else None

    insights_data: list[dict[str, Any]] = []
    if insight_table is not None:
        insights_result = await session.execute(
            select(insight_table)
            .where(insight_table.c.lead_id == lead_id)
            .order_by(insight_table.c.generated_at.desc())
        )
        insights_data = [dict(row) for row in insights_result.mappings().all()]

    text = _build_embedding_text(dict(lead_data), summary_data, insights_data)
    vector = await provider.generate_embedding(text)
    resolved_model = model_name or getattr(provider, "embedding_model", "unknown")

    new_id = uuid.uuid4()
    generated_at = datetime.now(timezone.utc)
    await session.execute(
        insert(embedding_table).values(
            id=new_id,
            lead_id=lead_id,
            embedding_vector=vector,
            model_name=resolved_model,
            generated_at=generated_at,
        )
    )
    await session.commit()
    return {
        "id": str(new_id),
        "lead_id": str(lead_id),
        "model_name": resolved_model,
        "generated_at": generated_at.isoformat(),
        "embedding_dim": len(vector),
    }


async def refresh_embeddings_for_all_leads(
    session: AsyncSession,
    provider: AIProvider,
    *,
    model_name: str | None = None,
) -> dict[str, Any]:
    metadata = MetaData()
    await session.run_sync(lambda sync_session: metadata.reflect(bind=sync_session.bind))
    leads = metadata.tables.get("leads")
    if leads is None:
        raise RuntimeError("leads table not found")

    result = await session.execute(select(leads.c.id))
    lead_ids = [row[0] for row in result.all()]

    success = 0
    failed = 0
    for lead_id in lead_ids:
        try:
            await generate_embedding_for_lead(
                session, provider, lead_id, model_name=model_name
            )
            success += 1
        except Exception:
            logger.exception("Failed to refresh embedding for lead %s", lead_id)
            failed += 1
    return {"total": len(lead_ids), "success": success, "failed": failed}
