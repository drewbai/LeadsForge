from functools import lru_cache
from pathlib import Path

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
        if v.startswith("postgresql://") and not v.startswith("postgresql+"):
            return "postgresql+asyncpg://" + v.removeprefix("postgresql://")
        if v.startswith("postgres://"):
            return "postgresql+asyncpg://" + v.removeprefix("postgres://")
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()