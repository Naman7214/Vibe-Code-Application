# Placeholder for settings.py

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "velocity_new"
    ERROR_COLLECTION_NAME: str = "error_logs"
    LLM_USAGE_COLLECTION_NAME: str = "llm_usage_logs"

    ANTHROPIC_DEFAULT_MODEL: str
    ANTHROPIC_API_KEY: str

    class Config:
        # Get the backend directory path relative to this config file
        # This config file is in: backend/app/config/settings.py
        # So we go up 2 levels to reach the backend folder
        backend_dir = Path(__file__).parent.parent.parent
        env_file = backend_dir / ".env"


settings = Settings()
