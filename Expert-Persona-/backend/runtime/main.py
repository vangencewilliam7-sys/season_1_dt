"""
runtime/main.py

FastAPI application entry point.

Dependency injection happens here — adapters, LLM providers, and readers
are instantiated once at startup and shared across all requests.

To switch domain: set DOMAIN_ADAPTER env var and restart.
To switch LLM: change the provider class in get_llm_*() functions.
To switch reader: change the factory in get_reader().
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from config.settings import settings
from runtime.api.extraction import router as extraction_router
from runtime.api.shadow import router as shadow_router

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── Dependency Singletons ─────────────────────────────────────────────────────
# These are instantiated once at startup. Import these functions
# anywhere in the app to get the active provider.

def get_adapter():
    """Return the active DomainAdapter based on DOMAIN_ADAPTER env var."""
    domain = settings.domain_adapter.lower()

    if domain == "generic":
        from adapters._reference_impl.generic_adapter import GenericAdapter
        return GenericAdapter()

    if domain == "recruiting":
        from adapters.recruiting.recruiting_adapter import RecruitingAdapter
        return RecruitingAdapter()
    if domain == "healthcare":
        from adapters.healthcare.healthcare_adapter import HealthcareAdapter
        return HealthcareAdapter()
    if domain == "tech_consulting":
        from adapters.tech_consulting.tech_consulting_adapter import TechConsultingAdapter
        return TechConsultingAdapter()

    raise ValueError(
        f"Unknown domain adapter: '{domain}'. "
        f"Check DOMAIN_ADAPTER env var. "
        f"Available: 'generic', 'recruiting', 'healthcare', 'tech_consulting'"
    )


def get_llm_ingestion():
    """Return the LLM provider for the Ingestion (Deep Scan) node."""
    if settings.llm_provider.lower() == "mock":
        from providers.mock_llm import MockLLMProvider
        return MockLLMProvider(model_id="mock-ingestion-llama-3.1-70b")

    from providers.groq_llm import GroqLLMProvider
    return GroqLLMProvider(
        api_key=settings.groq_api_key,
        model_id=settings.groq_ingestion_model,
    )


def get_llm_journalist():
    """Return the LLM provider for the Journalist (Adaptive Interviewer) node."""
    if settings.llm_provider.lower() == "mock":
        from providers.mock_llm import MockLLMProvider
        return MockLLMProvider(model_id="mock-journalist-llama-3.1-8b")

    from providers.groq_llm import GroqLLMProvider
    return GroqLLMProvider(
        api_key=settings.groq_api_key,
        model_id=settings.groq_journalist_model,
    )


# ── Knowledge Hub Services (singleton instances) ─────────────────────────────
# Initialised lazily at startup so we don't crash if credentials are missing.
_embedding_service = None
_vault_service = None


def get_embedding_service():
    """Return the singleton EmbeddingService for Knowledge Hub queries."""
    global _embedding_service
    if _embedding_service is None:
        from runtime.services.embedding_service import EmbeddingService
        _embedding_service = EmbeddingService(api_key=settings.openai_api_key)
    return _embedding_service


def get_vault_service():
    """Return the singleton KnowledgeVaultService for Knowledge Hub queries."""
    global _vault_service
    if _vault_service is None:
        from runtime.services.knowledge_vault import KnowledgeVaultService
        _vault_service = KnowledgeVaultService(
            supabase_url=settings.supabase_url,
            supabase_key=settings.supabase_service_role_key,
        )
    return _vault_service


def get_reader(reader_type: str = "filesystem", reader_config: dict = {}):
    """Return the appropriate DocumentReader based on request config."""
    if reader_type == "filesystem":
        from runtime.readers.filesystem_reader import FilesystemReader
        base_dir = reader_config.get("base_dir", "data")
        return FilesystemReader(base_dir=base_dir)

    if reader_type == "api":
        from runtime.readers.api_reader import APIReader
        return APIReader(
            base_url=reader_config.get("base_url"),
            token=reader_config.get("token")
        )

    if reader_type == "sql":
        from runtime.readers.sql_reader import SQLReader
        return SQLReader(
            connection_string=reader_config.get("connection_string"),
            table_name=reader_config.get("table_name", "expert_documents")
        )

    if reader_type == "supabase":
        from runtime.readers.supabase_reader import SupabaseReader
        return SupabaseReader(vault_service=get_vault_service())

    raise ValueError(
        f"Unknown reader type: '{reader_type}'. "
        f"Available: 'filesystem', 'api', 'sql', 'supabase'"
    )


# ── App Lifecycle ─────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup validation, then yield, then cleanup."""
    logger.info("=" * 60)
    logger.info("Universal Persona Extraction Framework")
    logger.info("=" * 60)

    # Validate the active adapter loads without error
    try:
        adapter = get_adapter()
        logger.info(f"Active domain adapter: {adapter.get_domain_id()}")
    except Exception as e:
        logger.error(f"Failed to load domain adapter: {e}")
        raise

    # Validate the LLM providers initialise
    try:
        ingestion_llm = get_llm_ingestion()
        journalist_llm = get_llm_journalist()
        logger.info(f"Ingestion LLM: {ingestion_llm.get_model_id()}")
        logger.info(f"Journalist LLM: {journalist_llm.get_model_id()}")
    except Exception as e:
        logger.error(f"Failed to initialise LLM providers: {e}")
        raise

    # Initialise Knowledge Hub integration services (non-blocking)
    try:
        vault = get_vault_service()
        embedder = get_embedding_service()
        hub_status = "connected" if vault.is_connected else "disconnected"
        logger.info(f"Knowledge Hub: {hub_status}")
    except Exception as e:
        logger.warning(f"Knowledge Hub integration unavailable: {e}")

    logger.info("Framework ready. API running.")
    logger.info("=" * 60)

    yield

    logger.info("Shutting down gracefully.")


# ── FastAPI App ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Universal Persona Extraction Framework",
    description=(
        "Extract high-fidelity PersonaManifests from expert Knowledge Hubs and Master Cases. "
        "Domain-agnostic, pluggable via DomainAdapter."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(extraction_router)
app.include_router(shadow_router)

# Serve the Shadow Mode Dashboard
@app.get("/dashboard")
async def dashboard_redirect(request: Request):
    return RedirectResponse(url="/dashboard/")

app.mount("/dashboard/", StaticFiles(directory="runtime/static", html=True), name="static")


@app.get("/health", tags=["System"])
async def health():
    """Health check endpoint."""
    adapter = get_adapter()
    vault = get_vault_service()
    return {
        "status": "healthy",
        "active_domain": adapter.get_domain_id(),
        "ingestion_model": settings.groq_ingestion_model,
        "journalist_model": settings.groq_journalist_model,
        "knowledge_hub": "connected" if vault.is_connected else "disconnected",
    }
