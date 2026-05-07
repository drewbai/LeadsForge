from app.enrichment.base import EnrichmentProvider

_FREE_DOMAINS = frozenset({"gmail.com", "yahoo.com", "outlook.com"})


class EmailQualityProvider(EnrichmentProvider):
    async def enrich(self, lead: dict) -> dict:
        result = dict(lead)
        email = result.get("email")
        if not email or not isinstance(email, str):
            return result

        if "+" in email:
            result["email_quality"] = "alias"
            return result

        domain = None
        if "@" in email:
            domain = email.split("@", 1)[1].strip().lower()
        elif (existing := result.get("email_domain")) and isinstance(existing, str):
            domain = existing.strip().lower()

        if domain and domain in _FREE_DOMAINS:
            result["email_quality"] = "free_provider"
        else:
            result["email_quality"] = "unknown"

        return result
