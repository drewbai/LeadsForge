from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import MetaData, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metric import METRIC_AI_INSIGHT_GENERATED
from app.services.ai.base import AIProvider
from app.services.metrics.service import fire_and_forget_increment
from app.services.ranking.triggers import enqueue_ranking_recompute

logger = logging.getLogger(__name__)


async def generate_insights_for_lead(
    session: AsyncSession,
    provider: AIProvider,
    lead_id: uuid.UUID,
    *,
    model_name: str | None = None,
) -> list[dict[str, Any]] | None:
    metadata = MetaData()
    await session.run_sync(lambda sync_session: metadata.reflect(bind=sync_session.bind))
    leads = metadata.tables.get("leads")
    insight_table = metadata.tables.get("lead_ai_insight")
    if leads is None or insight_table is None:
        raise RuntimeError("Required tables (leads, lead_ai_insight) not found")

    lead_row = await session.execute(select(leads).where(leads.c.id == lead_id))
    lead_data = lead_row.mappings().first()
    if lead_data is None:
        return None

    insights = await provider.generate_insights(dict(lead_data))
    if not insights:
        return []

    resolved_model = model_name or getattr(provider, "insight_model", "unknown")
    generated_at = datetime.now(timezone.utc)

    inserted: list[dict[str, Any]] = []
    for item in insights:
        new_id = uuid.uuid4()
        await session.execute(
            insert(insight_table).values(
                id=new_id,
                lead_id=lead_id,
                insight_type=item["insight_type"],
                insight_text=item["insight_text"],
                model_name=resolved_model,
                generated_at=generated_at,
            )
        )
        inserted.append(
            {
                "id": str(new_id),
                "lead_id": str(lead_id),
                "insight_type": item["insight_type"],
                "insight_text": item["insight_text"],
                "model_name": resolved_model,
                "generated_at": generated_at.isoformat(),
            }
        )
    await session.commit()
    await enqueue_ranking_recompute(lead_id)
    for item in inserted:
        await fire_and_forget_increment(
            METRIC_AI_INSIGHT_GENERATED,
            {
                "lead_id": str(lead_id),
                "model": resolved_model,
                "insight_type": item.get("insight_type"),
            },
        )
    return inserted


async def refresh_insights_for_all_leads(
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
    total_insights = 0
    for lead_id in lead_ids:
        try:
            inserted = await generate_insights_for_lead(session, provider, lead_id, model_name=model_name)
            success += 1
            total_insights += len(inserted or [])
        except Exception:
            logger.exception("Failed to refresh insights for lead %s", lead_id)
            failed += 1
    return {
        "total_leads": len(lead_ids),
        "success": success,
        "failed": failed,
        "insights_inserted": total_insights,
    }
