from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.env_data import DATABASE_URL as database_url

class Settings(BaseSettings):
    app_name: str = "Hireflow"
    database_url: str = database_url
    app_version: str = "1.0.0"
    environment: str = "development"
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()

def parse_cors_origins(value: str) -> list[str]:
    if not value:
        return ["http://localhost:5173"]

    return [origin.strip() for origin in value.split(",") if origin.strip()]