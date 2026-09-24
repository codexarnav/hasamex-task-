"""Core configuration module."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "InsightOS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://insightos:insightos@localhost:5432/insightos"

    @property
    def async_database_url(self) -> str:
        """Ensure the database URL has the postgresql+asyncpg:// scheme."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "research_utterances"

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "gemini-embedding-2"
    EMBEDDING_DIMENSION: int = 3072

    UPLOAD_DIR: str = "data/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50

    MAX_LLM_RETRIES: int = 2
    EVIDENCE_TOP_K: int = 20
    EVIDENCE_MIN_RELEVANCE: float = 0.5

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
