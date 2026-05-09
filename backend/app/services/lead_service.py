from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import lead_repository
from app.schemas.lead import LeadCreate
from app.services.events.activity import record_activity_event


async def create_lead(db: AsyncSession, lead_create: LeadCreate):
    lead = await lead_repository.insert_lead(db, lead_create)
    await record_activity_event(
        session=db,
        lead_id=lead.id,
        event_type="lead.created",
        payload={"email": lead.email, "source": lead.source},
        performed_by="system",
    )
    return lead


async def get_lead(db: AsyncSession, lead_id: UUID):
    return await lead_repository.select_lead_by_id(db, lead_id)


async def list_leads(db: AsyncSession):
    return await lead_repository.select_all_leads(db)
