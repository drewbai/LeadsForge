from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.models import IngestionResult
from app.ingestion.pipeline import run_ingestion
from app.ingestion.sources.csv_source import ingest_csv
from app.ingestion.sources.manual_source import ingest_manual


async def ingest_from_csv(file_path: str, db: AsyncSession) -> list[IngestionResult]:
    leads = await ingest_csv(file_path)
    return await run_ingestion(leads, db)


async def ingest_from_manual(leads: list[dict], db: AsyncSession) -> list[IngestionResult]:
    lead_inputs = await ingest_manual(leads)
    return await run_ingestion(lead_inputs, db)