from fastapi import APIRouter
from pydantic.v1 import BaseModel

from app.services import scoring_service


router = APIRouter(prefix="/scoring", tags=["scoring"])


class SingleLeadRequest(BaseModel):
    lead: dict


@router.post("/single")
async def score_single(request: SingleLeadRequest) -> dict:
    return await scoring_service.score_lead(request.lead)
