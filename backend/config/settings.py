"""
config/settings.py

Unified settings for the whole Digital Twin backend.
All modules import from here — no one reads os.environ directly.

SOLID — Single Responsibility + Dependency Inversion
Pydantic BaseSettings validates types and pulls from .env automatically.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """
    Single source of truth for all configuration.
    Add a new config key here + to .env — never read os.environ elsewhere.
    """

    # ── LLM Provider ──────────────────────────────────────────────────────────
    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")

    # OpenAI (primary)
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_ingestion_model: str = Field(
        default="gpt-4o", alias="OPENAI_INGESTION_MODEL"
    )
    openai_journalist_model: str = Field(
        default="gpt-4o-mini", alias="OPENAI_JOURNALIST_MODEL"
    )
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL"
    )

    # Groq (optional fallback)
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_ingestion_model: str = Field(
        default="llama-3.1-70b-versatile", alias="GROQ_INGESTION_MODEL"
    )
    groq_journalist_model: str = Field(
        default="llama-3.1-8b-instant", alias="GROQ_JOURNALIST_MODEL"
    )

    # ── Supabase ──────────────────────────────────────────────────────────────
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_service_role_key: str = Field(
        default="", alias="SUPABASE_SERVICE_ROLE_KEY"
    )
    supabase_anon_key: str = Field(
        default="", alias="SUPABASE_ANON_KEY"
    )

    # Table names
    supabase_chunks_table: str = Field(
        default="document_chunks", alias="SUPABASE_CHUNKS_TABLE"
    )
    supabase_master_cases_table: str = Field(
        default="master_cases", alias="SUPABASE_MASTER_CASES_TABLE"
    )
    supabase_manifests_table: str = Field(
        default="persona_manifests", alias="SUPABASE_MANIFESTS_TABLE"
    )
    supabase_pipeline_state_table: str = Field(
        default="pipeline_state", alias="SUPABASE_PIPELINE_STATE_TABLE"
    )

    # ── Expert Persona ─────────────────────────────────────────────────────────
    domain_adapter: str = Field(default="healthcare", alias="DOMAIN_ADAPTER")
    reader_type: str = Field(default="supabase", alias="READER_TYPE")
    filesystem_reader_base_dir: str = Field(
        default="data/expert_docs", alias="FILESYSTEM_READER_BASE_DIR"
    )

    # ── LangSmith ─────────────────────────────────────────────────────────────
    langchain_tracing_v2: bool = Field(default=False, alias="LANGCHAIN_TRACING_V2")
    langchain_api_key: Optional[str] = Field(default=None, alias="LANGCHAIN_API_KEY")
    langchain_project: str = Field(
        default="digital-twin-season-1", alias="LANGCHAIN_PROJECT"
    )

    # ── App ───────────────────────────────────────────────────────────────────
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # ── Convenience Properties ────────────────────────────────────────────────

    @property
    def active_ingestion_model(self) -> str:
        """Return the correct ingestion model for the active provider."""
        if self.llm_provider == "groq":
            return self.groq_ingestion_model
        return self.openai_ingestion_model

    @property
    def active_journalist_model(self) -> str:
        """Return the correct journalist model for the active provider."""
        if self.llm_provider == "groq":
            return self.groq_journalist_model
        return self.openai_journalist_model

    @property
    def active_api_key(self) -> str:
        """Return the API key for the active provider."""
        if self.llm_provider == "groq":
            return self.groq_api_key
        return self.openai_api_key

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "populate_by_name": True,
        "extra": "ignore",
    }


# Singleton — import this everywhere
settings = Settings()
