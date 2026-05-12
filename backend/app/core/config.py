"""
Application configuration using Pydantic BaseSettings.
All secrets are loaded from environment variables — never hardcoded.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "RecruitIQ"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Security
    secret_key: str = "change-me-in-production-use-long-random-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # Database
    database_url: str = "sqlite:///./recruitiq.db"

    # Embedding model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"

    # Optional LLM (provider-agnostic)
    llm_provider: Optional[str] = None       # "openai" | "anthropic" | None
    llm_api_key: Optional[str] = None
    llm_model: Optional[str] = None
    llm_base_url: Optional[str] = None       # for local/custom endpoints

    # FAISS index storage
    vector_store_path: str = "./data/faiss_index"

    # CORS — supply as a comma-separated string via env var:
    #   CORS_ORIGINS="https://recruitiq.vercel.app,https://example.com"
    # pydantic-settings parses this string field; main.py splits it at startup.
    cors_origins_str: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins_str.split(",") if o.strip()]

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
