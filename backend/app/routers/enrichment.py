from fastapi import APIRouter
from pydantic.v1 import BaseModel

from app.services import enrichment_service


router = APIRouter(prefix="/enrichment", tags=["enrichment"])


class SingleLeadRequest(BaseModel):
    lead: dict


@router.post("/single")
async def enrich_single(request: SingleLeadRequest) -> dict:
    return await enrichment_service.enrich_lead(request.lead)
