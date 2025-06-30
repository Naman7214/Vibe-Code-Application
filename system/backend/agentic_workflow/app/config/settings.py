import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "velocity_new"
    ERROR_COLLECTION_NAME: str = "error_logs"
    LLM_USAGE_COLLECTION_NAME: str = "llm_usage_logs"

    # Anthropic settings
    ANTHROPIC_API_KEY: str 
    ANTHROPIC_DEFAULT_MODEL: str 
    class Config:
        env_file = ".env"


# Create a global settings instance
settings = Settings()
