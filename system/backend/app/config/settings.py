import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "react_rocket"
    ERROR_COLLECTION_NAME: str = "error_logs"
    LLM_USAGE_COLLECTION_NAME: str = "llm_usage_logs"
    
    VOYAGEAI_API_KEY: str
    VOYAGEAI_BASE_URL: str
    
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    TAVILY_API_KEY: str

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
    ANTHROPIC_DEFAULT_MODEL: str
    OPENAI_BASE_URL: str = "https://api.openai.com/v1/chat/completions"
    OPENAI_MODEL: str = "gpt-4.1-mini-2025-04-14"
    SUMMARIZATION_TOKEN_THRESHOLD: int = 3500

    # HuggingFace settings
    HUGGINGFACE_API_KEY: str
    HUGGINGFACE_API_URL: str

    class Config:
        # Get the backend directory path relative to this config file
        # This config file is in: backend/app/config/settings.py
        # So we go up 2 levels to reach the backend folder
        backend_dir = Path(__file__).parent.parent.parent
        env_file = backend_dir / ".env"

settings = Settings()
