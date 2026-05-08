from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    APP_NAME: str = Field(default="LeadsForge")
    ENV: str = Field(default="development")
    DEBUG: bool = Field(default=False)


settings = Settings()