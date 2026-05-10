from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import AsyncSessionLocal
from app.models.lead import Lead
from app.schemas.lead import LeadCreate

SessionFactory = AsyncSessionLocal


async def insert_lead(db: AsyncSession, lead_create: LeadCreate) -> Lead:
    lead = Lead(email=lead_create.email, source=lead_create.source)
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


async def select_lead_by_id(db: AsyncSession, lead_id: UUID) -> Lead | None:
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    return result.scalar_one_or_none()


async def select_all_leads(db: AsyncSession) -> list[Lead]:
    result = await db.execute(select(Lead).order_by(Lead.created_at, Lead.id))
    return list(result.scalars().all())


async def update_lead(db: AsyncSession, lead_id: UUID, lead_update: LeadCreate) -> Lead | None:
    lead = await select_lead_by_id(db, lead_id)
    if lead is None:
        return None
    lead.email = lead_update.email
    lead.source = lead_update.source
    await db.commit()
    await db.refresh(lead)
    return lead


async def delete_lead(db: AsyncSession, lead_id: UUID) -> bool:
    lead = await select_lead_by_id(db, lead_id)
    if lead is None:
        return False
    await db.execute(delete(Lead).where(Lead.id == lead_id))
    await db.commit()
    return True
