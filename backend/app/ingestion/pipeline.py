from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.models import IngestionLeadInput, IngestionResult
from app.ingestion.normalizers import normalize_email, normalize_source
from app.ingestion.validators import validate_ingestion_lead
from app.schemas.lead import LeadCreate
from app.services import lead_service
from app.services.tasks.dispatcher import enqueue_ranking_recompute


async def run_ingestion(leads: list[IngestionLeadInput], db: AsyncSession) -> list[IngestionResult]:
    results: list[IngestionResult] = []

    for lead in leads:
        normalized_lead = IngestionLeadInput.construct(
            email=normalize_email(str(lead.email)),
            source=normalize_source(lead.source),
        )
        errors = validate_ingestion_lead(normalized_lead)

        if errors:
            results.append(IngestionResult(success=False, errors=errors))
            continue

        created = await lead_service.create_lead(
            db,
            LeadCreate(email=normalized_lead.email, source=normalized_lead.source),
        )
        if created is not None and getattr(created, "id", None) is not None:
            await enqueue_ranking_recompute(created.id)
        results.append(IngestionResult(success=True, errors=[]))

    return results
