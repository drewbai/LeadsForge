from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import MetaData, Table, delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai.base import AIProvider

logger = logging.getLogger(__name__)


def _summary_table() -> Table:
    metadata = MetaData()
    return Table("lead_ai_summary", metadata, autoload_replace=False, extend_existing=True)


async def _get_lead_dict(session: AsyncSession, lead_id: uuid.UUID) -> dict[str, Any] | None:
    metadata = MetaData()
    leads = Table("leads", metadata, autoload_replace=False, extend_existing=True)
    await session.run_sync(lambda sync_session: metadata.reflect(bind=sync_session.bind))
    leads = metadata.tables.get("leads")
    if leads is None:
        return None
    result = await session.execute(select(leads).where(leads.c.id == lead_id))
    row = result.mappings().first()
    if row is None:
        return None
    return dict(row)


async def generate_summary_for_lead(
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
    if leads is None or summary_table is None:
        raise RuntimeError("Required tables (leads, lead_ai_summary) not found")

    lead_row = await session.execute(select(leads).where(leads.c.id == lead_id))
    lead_data = lead_row.mappings().first()
    if lead_data is None:
        return None

    summary_text = await provider.generate_summary(dict(lead_data))
    resolved_model = model_name or getattr(provider, "summary_model", "unknown")

    await session.execute(delete(summary_table).where(summary_table.c.lead_id == lead_id))

    new_id = uuid.uuid4()
    generated_at = datetime.now(timezone.utc)
    await session.execute(
        insert(summary_table).values(
            id=new_id,
            lead_id=lead_id,
            summary_text=summary_text,
            model_name=resolved_model,
            generated_at=generated_at,
        )
    )
    await session.commit()
    return {
        "id": str(new_id),
        "lead_id": str(lead_id),
        "summary_text": summary_text,
        "model_name": resolved_model,
        "generated_at": generated_at.isoformat(),
    }


async def refresh_summaries_for_all_leads(
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
            await generate_summary_for_lead(session, provider, lead_id, model_name=model_name)
            success += 1
        except Exception:
            logger.exception("Failed to refresh summary for lead %s", lead_id)
            failed += 1
    return {"total": len(lead_ids), "success": success, "failed": failed}
