from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "velocity_new"
    ERROR_COLLECTION_NAME: str = "error_logs"
    LLM_USAGE_COLLECTION_NAME: str = "llm_usage_logs"
    ANTHROPIC_API_KEY: str
    ANTHROPIC_DEFAULT_MODEL: str = "claude-sonnet-4-20250514"
    OPENAI_API_KEY: str = "dummy_key"
    OPENAI_DEFAULT_MODEL: str = "o3-2025-04-16"

    # Tools API settings for IDE agent
    TOOLS_API_BASE_URL: str = "http://localhost:8001/api/v1"

    class Config:
        backend_dir = Path(__file__).parent.parent.parent
        env_file = backend_dir / ".env"


settings = Settings()
