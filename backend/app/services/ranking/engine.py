from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import MetaData, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.models.metric import METRIC_LEAD_RANKED
from app.services.metrics.service import fire_and_forget_increment

logger = logging.getLogger(__name__)


RANKING_WEIGHTS: dict[str, float] = {
    "activity": 0.30,
    "recency": 0.20,
    "enrichment": 0.15,
    "ai_insights": 0.20,
    "ai_summary": 0.15,
}


RANKING_THRESHOLDS: dict[str, Any] = {
    "max_activity_count": 50,
    "max_recency_days": 90,
    "summary_recency_days": 30,
}


INSIGHT_TYPE_WEIGHTS: dict[str, float] = {
    "next_best_action": 1.0,
    "opportunity": 0.9,
    "persona": 0.6,
    "sentiment": 0.4,
    "risk": -0.5,
}


def _score_bucket(score: float) -> str:
    if score >= 75.0:
        return "high"
    if score >= 35.0:
        return "mid"
    return "low"


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


async def _activity_score(
    session: AsyncSession,
    lead_id: uuid.UUID,
    metadata: MetaData,
) -> tuple[float, dict[str, Any]]:
    activity_table = metadata.tables.get("lead_activity_log")
    if activity_table is None:
        return 0.0, {"activity_count": 0}
    result = await session.execute(
        select(func.count()).select_from(activity_table).where(activity_table.c.lead_id == lead_id)
    )
    count = int(result.scalar() or 0)
    max_count = float(RANKING_THRESHOLDS["max_activity_count"])
    score = _clamp01(count / max_count) if max_count > 0 else 0.0
    return score, {"activity_count": count}


async def _recency_score(
    session: AsyncSession,
    lead_id: uuid.UUID,
    metadata: MetaData,
) -> tuple[float, dict[str, Any]]:
    activity_table = metadata.tables.get("lead_activity_log")
    if activity_table is None:
        return 0.0, {"days_since_last_activity": None}
    result = await session.execute(
        select(func.max(activity_table.c.created_at)).where(activity_table.c.lead_id == lead_id)
    )
    last_at = result.scalar()
    if last_at is None:
        return 0.0, {"days_since_last_activity": None}
    if last_at.tzinfo is None:
        last_at = last_at.replace(tzinfo=timezone.utc)
    delta_days = (datetime.now(timezone.utc) - last_at).total_seconds() / 86400.0
    max_days = float(RANKING_THRESHOLDS["max_recency_days"])
    if max_days <= 0:
        return 0.0, {"days_since_last_activity": delta_days}
    score = _clamp01(1.0 - (delta_days / max_days))
    return score, {"days_since_last_activity": delta_days}


async def _enrichment_score(
    session: AsyncSession,
    lead_id: uuid.UUID,
    metadata: MetaData,
) -> tuple[float, dict[str, Any]]:
    leads = metadata.tables.get("leads")
    if leads is None:
        return 0.0, {"enriched_fields": 0}
    result = await session.execute(select(leads).where(leads.c.id == lead_id))
    row = result.mappings().first()
    if row is None:
        return 0.0, {"enriched_fields": 0}
    fields = ("full_name", "email", "phone", "source", "status", "notes")
    available = [f for f in fields if f in row]
    if not available:
        return 0.0, {"enriched_fields": 0, "considered": 0}
    filled = sum(1 for f in available if row.get(f))
    score = _clamp01(filled / len(available))
    return score, {"enriched_fields": filled, "considered": len(available)}


async def _ai_insight_score(
    session: AsyncSession,
    lead_id: uuid.UUID,
    metadata: MetaData,
) -> tuple[float, dict[str, Any]]:
    insight_table = metadata.tables.get("lead_ai_insight")
    if insight_table is None:
        return 0.0, {"insight_count": 0}
    result = await session.execute(select(insight_table.c.insight_type).where(insight_table.c.lead_id == lead_id))
    types = [row[0] for row in result.all()]
    if not types:
        return 0.0, {"insight_count": 0}
    raw = sum(INSIGHT_TYPE_WEIGHTS.get(t, 0.0) for t in types)
    normalized = (raw / len(types) + 1.0) / 2.0
    return _clamp01(normalized), {"insight_count": len(types), "raw": raw}


async def _ai_summary_score(
    session: AsyncSession,
    lead_id: uuid.UUID,
    metadata: MetaData,
) -> tuple[float, dict[str, Any]]:
    summary_table = metadata.tables.get("lead_ai_summary")
    if summary_table is None:
        return 0.0, {"summary_present": False}
    result = await session.execute(
        select(summary_table.c.generated_at)
        .where(summary_table.c.lead_id == lead_id)
        .order_by(summary_table.c.generated_at.desc())
        .limit(1)
    )
    generated_at = result.scalar()
    if generated_at is None:
        return 0.0, {"summary_present": False}
    if generated_at.tzinfo is None:
        generated_at = generated_at.replace(tzinfo=timezone.utc)
    days = (datetime.now(timezone.utc) - generated_at).total_seconds() / 86400.0
    max_days = float(RANKING_THRESHOLDS["summary_recency_days"])
    if max_days <= 0:
        return 1.0, {"summary_present": True, "summary_age_days": days}
    score = _clamp01(1.0 - (days / max_days))
    return max(score, 0.5), {
        "summary_present": True,
        "summary_age_days": days,
    }


async def compute_lead_ranking(
    session: AsyncSession,
    lead_id: uuid.UUID,
) -> dict[str, Any] | None:
    if isinstance(lead_id, str):
        lead_id = uuid.UUID(lead_id)

    metadata = MetaData()
    await session.run_sync(lambda sync_session: metadata.reflect(bind=sync_session.bind))
    leads = metadata.tables.get("leads")
    if leads is None:
        raise RuntimeError("leads table not found")

    lead_record = await session.get(Lead, lead_id)
    if lead_record is None:
        return None

    activity_score, activity_meta = await _activity_score(session, lead_id, metadata)
    recency_score, recency_meta = await _recency_score(session, lead_id, metadata)
    enrichment_score, enrichment_meta = await _enrichment_score(session, lead_id, metadata)
    insight_score, insight_meta = await _ai_insight_score(session, lead_id, metadata)
    summary_score, summary_meta = await _ai_summary_score(session, lead_id, metadata)

    components = {
        "activity": activity_score,
        "recency": recency_score,
        "enrichment": enrichment_score,
        "ai_insights": insight_score,
        "ai_summary": summary_score,
    }
    total = sum(components[key] * RANKING_WEIGHTS.get(key, 0.0) for key in components)
    final_score = round(_clamp01(total) * 100.0, 2)

    explanation_parts = [
        f"activity={activity_score:.2f}",
        f"recency={recency_score:.2f}",
        f"enrichment={enrichment_score:.2f}",
        f"ai_insights={insight_score:.2f}",
        f"ai_summary={summary_score:.2f}",
    ]
    explanation = " | ".join(explanation_parts)

    now = datetime.now(timezone.utc)
    lead_record.ranking_score = final_score
    lead_record.ranking_explanation = explanation
    lead_record.last_ranked_at = now
    await session.commit()

    await fire_and_forget_increment(
        METRIC_LEAD_RANKED,
        {"lead_id": str(lead_id), "score_bucket": _score_bucket(final_score)},
    )

    return {
        "lead_id": str(lead_id),
        "ranking_score": final_score,
        "ranking_explanation": explanation,
        "last_ranked_at": now.isoformat(),
        "components": components,
        "weights": RANKING_WEIGHTS,
        "details": {
            "activity": activity_meta,
            "recency": recency_meta,
            "enrichment": enrichment_meta,
            "ai_insights": insight_meta,
            "ai_summary": summary_meta,
        },
    }


async def recompute_ranking_for_all_leads(
    session: AsyncSession,
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
            await compute_lead_ranking(session, lead_id)
            success += 1
        except Exception:
            logger.exception("Failed to compute ranking for lead %s", lead_id)
            failed += 1
    return {"total": len(lead_ids), "success": success, "failed": failed}
