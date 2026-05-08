from pydantic import BaseModel, EmailStr


class IngestionLeadInput(BaseModel):
    email: EmailStr
    source: str


class IngestionResult(BaseModel):
    success: bool
    errors: list[str]
