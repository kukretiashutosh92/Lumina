"""
Application configuration.

This version uses hardcoded defaults only.
No environment variables required.
"""

from pydantic import BaseModel


class Settings(BaseModel):
    # Database
    db_url: str = "postgresql+asyncpg://luminalib:luminalib@localhost:5432/luminalib"

    # Authentication
    secret_key: str = "dev-secret-key"
    token_expire_minutes: int = 60

    # Storage
    storage_backend: str = "local"
    local_storage_path: str = "./uploads"
    aws_bucket: str = ""
    aws_region: str = "us-east-1"

    # LLM
    llm_provider: str = "mock"  # mock | ollama | openai
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Recommendation Engine
    recommendation_engine: str = "hybrid"  # hybrid | llm


# Global config instance
settings = Settings()