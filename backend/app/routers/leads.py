from collections.abc import AsyncIterator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import AsyncSessionLocal
from app.schemas.lead import LeadCreate, LeadRead
from app.services import lead_service


router = APIRouter(prefix="/leads", tags=["leads"])


async def get_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


get_session = get_db

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_create: LeadCreate,
    db: DbSession,
) -> LeadRead:
    lead = await lead_service.create_lead(db, lead_create)
    return LeadRead.model_validate(lead)


@router.get("/")
async def list_leads(db: DbSession) -> list[LeadRead]:
    leads = await lead_service.list_leads(db)
    return [LeadRead.model_validate(lead) for lead in leads]


@router.get("/db-test")
async def db_test(session: AsyncSession = Depends(get_session)):
    result = await session.execute(text("SELECT NOW()"))
    return {"db_time": result.scalar()}


@router.get("/{lead_id}")
async def get_lead(lead_id: UUID, db: DbSession) -> LeadRead:
    lead = await lead_service.get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    return LeadRead.model_validate(lead)