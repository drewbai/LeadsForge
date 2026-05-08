from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion import tasks
from app.ingestion.models import IngestionResult


async def ingest_csv_file(file_path: str, db: AsyncSession) -> list[IngestionResult]:
    return await tasks.ingest_from_csv(file_path, db)


async def ingest_manual_payload(leads: list[dict], db: AsyncSession) -> list[IngestionResult]:
    return await tasks.ingest_from_manual(leads, db)
