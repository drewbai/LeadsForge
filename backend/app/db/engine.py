import ssl
from typing import AsyncIterator
from urllib.parse import parse_qsl, urlparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.settings import get_settings


def _asyncpg_connect_args(database_url: str) -> dict:
    """asyncpg needs explicit TLS for Neon; ssl=True is flaky on some Windows stacks."""
    parsed = urlparse(database_url)
    host = (parsed.hostname or "").lower()
    qs = {k.lower(): val for k, val in parse_qsl(parsed.query, keep_blank_values=True)}
    sslmode = (qs.get("sslmode") or "").lower()
    ssl_q = (qs.get("ssl") or "").lower()
    if (
        host.endswith(".neon.tech")
        or sslmode in ("require", "verify-ca", "verify-full")
        or ssl_q in ("true", "1", "require")
    ):
        return {"ssl": ssl.create_default_context()}
    return {}


settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
    connect_args=_asyncpg_connect_args(settings.DATABASE_URL),
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
