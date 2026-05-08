from fastapi import APIRouter

from app.schemas.lead_pipeline import LeadRecord, SingleLeadRequest
from app.services import enrichment_service

router = APIRouter(prefix="/enrichment", tags=["enrichment"])


@router.post("/single", response_model=LeadRecord)
async def enrich_single(request: SingleLeadRequest) -> LeadRecord:
    data = await enrichment_service.enrich_lead(request.lead)
    return LeadRecord.model_validate(data)
