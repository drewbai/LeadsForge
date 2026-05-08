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
