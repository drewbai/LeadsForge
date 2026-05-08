from fastapi import APIRouter

from app.schemas.lead_pipeline import LeadRecord, SingleLeadRequest
from app.services import scoring_service

router = APIRouter(prefix="/scoring", tags=["scoring"])


@router.post("/single", response_model=LeadRecord)
async def score_single(request: SingleLeadRequest) -> LeadRecord:
    data = await scoring_service.score_lead(request.lead)
    return LeadRecord.model_validate(data)
