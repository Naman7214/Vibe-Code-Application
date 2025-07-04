from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "velocity_tools"
    ERROR_COLLECTION_NAME: str = "error_logs"
    LLM_USAGE_COLLECTION_NAME: str = "llm_usage_logs"

    # Relace API settings
    RELACE_API_KEY: str = "dummy_key"
    RELACE_API_URL: str = (
        "https://instantapply.endpoint.relace.run/v1/code/apply"
    )

    class Config:
        env_file = ".env"


settings = Settings()
