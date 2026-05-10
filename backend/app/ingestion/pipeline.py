from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.models import IngestionLeadInput, IngestionResult
from app.ingestion.normalizers import normalize_email, normalize_source
from app.ingestion.validators import validate_ingestion_lead
from app.schemas.lead import LeadCreate
from app.services import lead_service


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

        await lead_service.create_lead(
            db,
            LeadCreate(email=normalized_lead.email, source=normalized_lead.source),
        )
        results.append(IngestionResult(success=True, errors=[]))

    return results
