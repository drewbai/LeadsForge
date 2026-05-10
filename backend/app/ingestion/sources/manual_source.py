import asyncio
from typing import Any

from app.ingestion.models import IngestionLeadInput


def _build_manual_inputs(leads: list[dict[str, Any]]) -> list[IngestionLeadInput]:
    return [
        IngestionLeadInput.construct(
            email=lead.get("email", ""),
            source=lead.get("source", ""),
        )
        for lead in leads
    ]


async def ingest_manual(leads: list[dict[str, Any]]) -> list[IngestionLeadInput]:
    return await asyncio.to_thread(_build_manual_inputs, leads)
