from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", case_sensitive=False)

    APP_NAME: str = Field(default="LeadsForge")
    ENV: str = Field(default="dev")
    DEBUG: bool = Field(default=False)
    DATABASE_URL: str = Field(default="postgresql+asyncpg://dev:dev@localhost:5432/leadsforge")

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_async_database_url(cls, v: object) -> object:
        """Neon/docs often use postgresql://… without a driver; async engine needs asyncpg."""
        if not isinstance(v, str):
            return v
        url = v
        if url.startswith("postgresql://") and not url.startswith("postgresql+"):
            url = "postgresql+asyncpg://" + url.removeprefix("postgresql://")
        elif url.startswith("postgres://"):
            url = "postgresql+asyncpg://" + url.removeprefix("postgres://")
        if url.startswith("postgresql+"):
            parsed = urlparse(url)
            host = (parsed.hostname or "").lower()
            # channel_binding is libpq-only and breaks asyncpg.
            skip = {"channel_binding"}
            # Neon URLs may carry libpq ssl=* params; asyncpg uses engine connect_args for TLS.
            if host.endswith(".neon.tech"):
                skip |= {
                    "sslmode",
                    "sslcert",
                    "sslkey",
                    "sslrootcert",
                    "sslcrl",
                }
            q = [(k, val) for k, val in parse_qsl(parsed.query, keep_blank_values=True) if k.lower() not in skip]
            url = urlunparse(parsed._replace(query=urlencode(q)))
        return url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
