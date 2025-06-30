from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "velocity_tools"
    ERROR_COLLECTION_NAME: str = "error_logs"
    LLM_USAGE_COLLECTION_NAME: str = "llm_usage_logs"

    VOYAGEAI_API_KEY: str = "dummy_key"
    VOYAGEAI_BASE_URL: str = "dummy_url"

    OPENAI_API_KEY: str = "dummy_key"
    PINECONE_API_KEY: str = "dummy_key"
    TAVILY_API_KEY: str = "dummy_key"

    # Pinecone settings
    PINECONE_CREATE_INDEX_URL: str = "https://api.pinecone.io/indexes"
    PINECONE_API_VERSION: str = "2025-01"
    PINECONE_EMBED_URL: str = "https://api.pinecone.io/embed"
    PINECONE_UPSERT_URL: str = "https://{}/vectors/upsert"
    PINECONE_RERANK_URL: str = "https://api.pinecone.io/rerank"
    PINECONE_QUERY_URL: str = "https://{}/query"
    PINECONE_LIST_INDEXES_URL: str = "https://api.pinecone.io/indexes"
    PINECONE_INDEX_NAME: str = "n8n-examples"
    PINECONE_SIMILARITY_THRESHOLD: float = 0.56
    ANTHROPIC_API_KEY: str
    ANTHROPIC_BASE_URL: str = "https://api.anthropic.com/v1/messages"
    ANTHROPIC_DEFAULT_MODEL: str = "claude-sonnet-4-20250514"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1/chat/completions"
    OPENAI_MODEL: str = "gpt-4.1-mini-2025-04-14"
    SUMMARIZATION_TOKEN_THRESHOLD: int = 3500

    # HuggingFace settings
    HUGGINGFACE_API_KEY: str = "dummy_key"
    HUGGINGFACE_API_URL: str = "dummy_url"

    class Config:
        env_file = ".env"


settings = Settings()
