from pydantic.v1 import BaseSettings, Field


class Settings(BaseSettings):
    APP_NAME: str = Field(default="LeadsForge")
    ENV: str = Field(default="development")
    DEBUG: bool = Field(default=False)

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()