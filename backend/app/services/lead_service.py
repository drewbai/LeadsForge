from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.models.metric import METRIC_LEAD_CREATED
from app.repositories import lead_repository
from app.schemas.lead import LeadCreate
from app.services.events.activity import record_activity_event
from app.services.metrics.service import fire_and_forget_increment
from app.services.ranking.triggers import enqueue_ranking_recompute


async def create_lead(db: AsyncSession, lead_create: LeadCreate) -> Lead:
    lead = await lead_repository.insert_lead(db, lead_create)
    await enqueue_ranking_recompute(lead.id)
    await fire_and_forget_increment(
        METRIC_LEAD_CREATED,
        {"source": lead.source} if lead.source else None,
    )
    await record_activity_event(
        session=db,
        lead_id=lead.id,
        event_type="lead.created",
        payload={"email": lead.email, "source": lead.source},
        performed_by="system",
    )
    return lead


async def update_lead(db: AsyncSession, lead_id: UUID, lead_update: LeadCreate) -> Lead | None:
    lead = await lead_repository.update_lead(db, lead_id, lead_update)
    if lead is not None:
        await enqueue_ranking_recompute(lead.id)
    return lead


async def delete_lead(db: AsyncSession, lead_id: UUID) -> bool:
    return await lead_repository.delete_lead(db, lead_id)


async def get_lead(db: AsyncSession, lead_id: UUID) -> Lead | None:
    return await lead_repository.select_lead_by_id(db, lead_id)


async def list_leads(db: AsyncSession) -> list[Lead]:
    return await lead_repository.select_all_leads(db)
