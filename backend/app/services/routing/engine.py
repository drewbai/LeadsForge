from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import MetaData, select, update
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


RANKING_HIGH_THRESHOLD: float = 75.0
RANKING_LOW_THRESHOLD: float = 35.0


HIGH_INTENT_INSIGHT_TYPES: frozenset[str] = frozenset(
    {"next_best_action", "opportunity"}
)
RISK_INSIGHT_TYPES: frozenset[str] = frozenset({"risk"})


HIGH_VALUE_INDUSTRIES: frozenset[str] = frozenset(
    {"saas", "fintech", "healthcare", "enterprise"}
)
HIGH_VALUE_COMPANY_SIZES: frozenset[str] = frozenset({"large", "enterprise"})


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _normalize(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _classify(
    score: float,
    *,
    has_high_intent: bool,
    has_risk: bool,
    has_high_value_enrichment: bool,
) -> tuple[str, list[str]]:
    notes: list[str] = []

    if score >= RANKING_HIGH_THRESHOLD and has_high_intent:
        bucket = "priority"
        notes.append(f"high score ({score:.1f}) + high-intent insight")
    elif score >= RANKING_HIGH_THRESHOLD:
        bucket = "priority"
        notes.append(f"high score ({score:.1f})")
    elif score >= RANKING_LOW_THRESHOLD and has_high_intent:
        bucket = "priority"
        notes.append(f"mid score ({score:.1f}) elevated by high-intent insight")
    elif score >= RANKING_LOW_THRESHOLD:
        bucket = "standard"
        notes.append(f"mid score ({score:.1f})")
    else:
        bucket = "nurture"
        notes.append(f"low score ({score:.1f})")

    if has_high_value_enrichment:
        notes.append("high-value enrichment match")
        if bucket == "nurture":
            bucket = "standard"
            notes.append("upgraded nurture -> standard on enrichment")

    if has_risk:
        notes.append("risk insight present")
        if bucket == "priority":
            bucket = "standard"
            notes.append("downgraded priority -> standard on risk")

    return bucket, notes


async def _load_metadata(session: AsyncSession) -> MetaData:
    metadata = MetaData()
    await session.run_sync(lambda sync_session: metadata.reflect(bind=sync_session.bind))
    return metadata


async def route_lead(
    session: AsyncSession,
    lead_id: uuid.UUID,
) -> dict[str, Any] | None:
    metadata = await _load_metadata(session)
    leads = metadata.tables.get("leads")
    if leads is None:
        raise RuntimeError("leads table not found")

    lead_result = await session.execute(select(leads).where(leads.c.id == lead_id))
    lead_row = lead_result.mappings().first()
    if lead_row is None:
        return None

    score = _to_float(lead_row.get("ranking_score") if "ranking_score" in lead_row else 0.0)

    insight_types: list[str] = []
    insight_table = metadata.tables.get("lead_ai_insight")
    if insight_table is not None:
        insight_result = await session.execute(
            select(insight_table.c.insight_type).where(
                insight_table.c.lead_id == lead_id
            )
        )
        insight_types = [row[0] for row in insight_result.all() if row[0]]

    has_high_intent = any(t in HIGH_INTENT_INSIGHT_TYPES for t in insight_types)
    has_risk = any(t in RISK_INSIGHT_TYPES for t in insight_types)

    industry = _normalize(lead_row.get("industry"))
    company_size = _normalize(lead_row.get("company_size"))
    has_high_value_enrichment = (
        industry in HIGH_VALUE_INDUSTRIES or company_size in HIGH_VALUE_COMPANY_SIZES
    )

    bucket, notes = _classify(
        score,
        has_high_intent=has_high_intent,
        has_risk=has_risk,
        has_high_value_enrichment=has_high_value_enrichment,
    )

    reason = " | ".join(notes)
    now = datetime.now(timezone.utc)

    update_values: dict[str, Any] = {}
    if "assigned_to" in leads.c:
        update_values["assigned_to"] = bucket
    if "routing_reason" in leads.c:
        update_values["routing_reason"] = reason
    if "last_routed_at" in leads.c:
        update_values["last_routed_at"] = now

    if update_values:
        await session.execute(
            update(leads).where(leads.c.id == lead_id).values(**update_values)
        )
        await session.commit()

    return {
        "lead_id": str(lead_id),
        "assigned_to": bucket,
        "reason": reason,
        "last_routed_at": now.isoformat(),
        "signals": {
            "ranking_score": score,
            "insight_types": insight_types,
            "has_high_intent": has_high_intent,
            "has_risk": has_risk,
            "industry": industry or None,
            "company_size": company_size or None,
        },
    }


async def trigger_routing(lead_id: uuid.UUID) -> dict[str, Any] | None:
    if lead_id is None:
        return None
    from app.db.engine import AsyncSessionLocal

    try:
        async with AsyncSessionLocal() as session:
            return await route_lead(session, lead_id)
    except Exception:
        logger.exception("Routing failed for lead %s", lead_id)
        return None
