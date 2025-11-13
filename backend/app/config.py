"""
Configuration settings for the Portfolio Chatbot application.
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Configuration
    OPENAI_API_KEY: str = "not-needed-for-free-models"  # Optional now
    USE_FREE_MODEL: bool = True  # Set to True for free models (HuggingFace)
    FREE_MODEL_TYPE: str = "huggingface"  # "huggingface" or "groq"
    GROQ_API_KEY: str = ""  # Get free key from console.groq.com
    
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
    
    # LLM Settings (ignored if USE_FREE_MODEL=True)
    LLM_MODEL: str = "gpt-3.5-turbo"
    FALLBACK_MODEL: str = "gpt-3.5-turbo"

    # Free Model Settings
    FREE_MODEL_NAME: str = "google/flan-t5-large"  # Free HuggingFace model
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 20
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()