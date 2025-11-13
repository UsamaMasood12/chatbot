"""
Configuration settings for the Portfolio Chatbot application.
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    
    # Application Settings
    APP_NAME: str = "Portfolio Chatbot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    
    # Vector Store Settings
    VECTOR_STORE_TYPE: str = "faiss"  # chromadb or faiss (use faiss on Windows)
    VECTOR_STORE_PATH: str = "./vector_store"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # RAG Settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 3
    TEMPERATURE: float = 0.2  # Low temperature for consistent, factual answers
    MAX_TOKENS: int = 500
    
    # LLM Settings
    LLM_MODEL: str = "gpt-4"
    FALLBACK_MODEL: str = "gpt-3.5-turbo"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 20
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()