from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class LeadCreate(BaseModel):
    email: EmailStr
    source: str


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    source: str
    created_at: datetime
    ranking_score: float | None = None
    ranking_explanation: str | None = None
    last_ranked_at: datetime | None = None
    assigned_to: str | None = None
    routing_reason: str | None = None
    last_routed_at: datetime | None = None
