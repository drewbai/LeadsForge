import asyncio
import csv

from app.ingestion.models import IngestionLeadInput


def _read_csv(file_path: str) -> list[IngestionLeadInput]:
    leads: list[IngestionLeadInput] = []

    with open(file_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            leads.append(
                IngestionLeadInput.construct(
                    email=row.get("email", ""),
                    source=row.get("source", ""),
                )
            )

    return leads


async def ingest_csv(file_path: str) -> list[IngestionLeadInput]:
    return await asyncio.to_thread(_read_csv, file_path)