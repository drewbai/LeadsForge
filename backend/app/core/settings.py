from functools import lru_cache

from pydantic.v1 import BaseSettings, Field


class Settings(BaseSettings):
    APP_NAME: str = Field(default="LeadsForge")
    ENV: str = Field(default="dev")
    DEBUG: bool = Field(default=False)
    DATABASE_URL: str = Field(default="postgresql+asyncpg://dev:dev@localhost:5432/leadsforge")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()