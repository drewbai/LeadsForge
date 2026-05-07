from app.ingestion.models import IngestionLeadInput


def validate_ingestion_lead(lead: IngestionLeadInput) -> list[str]:
    errors: list[str] = []

    if not str(lead.email).strip():
        errors.append("email is required")

    if not lead.source.strip():
        errors.append("source is required")

    return errors