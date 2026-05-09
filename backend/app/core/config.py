from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = Field(default="LeadsForge")
    ENV: str = Field(default="development")
    DEBUG: bool = Field(default=False)

    AI_PROVIDER: str = Field(default="openai")
    OPENAI_API_KEY: str | None = Field(default=None)
    OPENAI_SUMMARY_MODEL: str = Field(default="gpt-4o-mini")
    OPENAI_INSIGHT_MODEL: str = Field(default="gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small")
    OPENAI_EMBEDDING_DIM: int = Field(default=1536)


settings = Settings()
