import asyncio

from app.ingestion.models import IngestionLeadInput


def _build_manual_inputs(leads: list[dict]) -> list[IngestionLeadInput]:
    return [
        IngestionLeadInput.construct(
            email=lead.get("email", ""),
            source=lead.get("source", ""),
        )
        for lead in leads
    ]


async def ingest_manual(leads: list[dict]) -> list[IngestionLeadInput]:
    return await asyncio.to_thread(_build_manual_inputs, leads)
