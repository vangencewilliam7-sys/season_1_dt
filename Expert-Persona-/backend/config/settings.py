from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "mock" # "groq" or "mock"
    groq_api_key: Optional[str] = None
    groq_ingestion_model: str = "llama-3.1-70b-versatile"
    groq_journalist_model: str = "llama-3.1-8b-instant"

    # Database (LangGraph checkpointing only)
    database_url: str = "postgresql://persona_user:persona_pass@localhost:5432/persona_db"

    # LangSmith
    langchain_tracing_v2: bool = False
    langchain_api_key: Optional[str] = None
    langchain_project: str = "persona-extraction"

    # App
    app_env: str = "development"
    log_level: str = "INFO"

    # Domain adapter slug to instantiate at startup
    domain_adapter: str = "generic"

    # ── Knowledge Hub Integration ──────────────────────────────────────────
    # Supabase credentials (shared with the Knowledge Hub repo)
    supabase_url: Optional[str] = None
    supabase_service_role_key: Optional[str] = None

    # OpenAI API key (used for embeddings — must match KH's embedding model)
    openai_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton — import this everywhere
settings = Settings()
