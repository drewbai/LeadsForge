from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    APP_NAME: str = Field(default="LeadsForge")
    ENV: str = Field(default="dev")
    DEBUG: bool = Field(default=False)
    DATABASE_URL: str = Field(default="postgresql+asyncpg://dev:dev@localhost:5432/leadsforge")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()