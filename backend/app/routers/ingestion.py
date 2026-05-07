from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic.v1 import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import AsyncSessionLocal
from app.ingestion.models import IngestionResult
from app.services import ingestion_service


router = APIRouter(prefix="/ingestion", tags=["ingestion"])


class CsvIngestionRequest(BaseModel):
    file_path: str


class ManualIngestionRequest(BaseModel):
    leads: list[dict]


async def get_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.post("/csv")
async def ingest_csv(request: CsvIngestionRequest, db: DbSession) -> list[IngestionResult]:
    return await ingestion_service.ingest_csv_file(request.file_path, db)


@router.post("/manual")
async def ingest_manual(request: ManualIngestionRequest, db: DbSession) -> list[IngestionResult]:
    return await ingestion_service.ingest_manual_payload(request.leads, db)