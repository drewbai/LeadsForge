from datetime import datetime
from uuid import UUID

from pydantic.v1 import BaseModel, EmailStr


class LeadCreate(BaseModel):
    email: EmailStr
    source: str


class LeadRead(BaseModel):
    id: UUID
    email: EmailStr
    source: str
    created_at: datetime

    class Config:
        orm_mode = True