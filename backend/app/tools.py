"""
tools.py — Logic Vault Retrieval Tools
========================================
@tool-decorated functions designed to be injected as Tool Nodes into
Vardhan's LangGraph graph once the Knowledge Hub is connected.

CRITICAL RULE: All functions return plain Python dicts — never LangChain
Document objects — so Vardhan's GraphState stays fully JSON-serializable.

Current usage: These tools are ready to use but are not called anywhere
inside the Knowledge Hub pipeline itself. The Knowledge Hub's job is to
BUILD the Logic Vault. These tools QUERY it (Phase 5 / Vardhan's graph).
"""

from langchain_core.tools import tool
from .services.embeddings import EmbeddingService
from .services.supabase_client import SupabaseService

# Initialize services once at module level (not per-call)
_embedder = EmbeddingService()
_db = SupabaseService()

# Clearance-based confidence thresholds
# Doctors see more results (lower threshold), patients see fewer (safer)
_CLEARANCE_THRESHOLDS: dict = {
    "doctor":  0.70,
    "nurse":   0.75,
    "patient": 0.85,
}
_DEFAULT_THRESHOLD = 0.75


@tool
def retrieve_expert_knowledge(
    query: str,
    domain_id: str,
    role_name: str,
    persona_clearance: str
) -> dict:
    """
    Retrieve the most relevant human-verified expert decision from the Logic Vault.

    Searches ONLY the expert_dna table (high-purity, human-approved records).
    Results are filtered by domain_id FK — no cross-twin contamination possible.

    Args:
        query:             User question or scenario description.
        domain_id:         UUID FK from the `domains` table (from the active adapter).
        role_name:         Human-readable role name for logging (e.g., 'Doctor').
        persona_clearance: Requester role for threshold tuning (e.g., 'doctor', 'patient').

    Returns:
        Plain dict with: found, expert_decision, impact_archetype,
        similarity, reasoning, domain_id, role_name, message.
    """
    try:
        query_vector = _embedder.get_embedding(query)
        threshold = _CLEARANCE_THRESHOLDS.get(persona_clearance.lower(), _DEFAULT_THRESHOLD)

        # Pass domain_id FK — deterministic filter, not a text match
        results = _db.expert_vault_search(query_vector, domain_id=domain_id, limit=3)

        # Apply clearance-based threshold
        results = [r for r in results if r.get("similarity", 0) >= threshold]

        if not results:
            return {
                "found":            False,
                "expert_decision":  None,
                "impact_archetype": None,
                "similarity":       0.0,
                "reasoning":        None,
                "domain_id":        domain_id,
                "role_name":        role_name,
                "message": (
                    f"No verified expert logic found for domain_id='{domain_id}' "
                    f"role='{role_name}' above threshold={threshold} "
                    f"(clearance='{persona_clearance}'). "
                    f"This query may need human escalation."
                )
            }

        top = results[0]
        return {
            "found":            True,
            "expert_decision":  top.get("expert_decision"),
            "impact_archetype": top.get("impact_archetype"),
            "similarity":       round(top.get("similarity", 0), 4),
            "reasoning":        top.get("reasoning"),
            "domain_id":        domain_id,
            "role_name":        role_name,
            "message":          "Expert logic retrieved from Logic Vault."
        }

    except Exception as e:
        return {
            "found":            False,
            "expert_decision":  None,
            "impact_archetype": None,
            "similarity":       0.0,
            "reasoning":        None,
            "domain_id":        domain_id,
            "role_name":        role_name,
            "message":          f"Retrieval error: {str(e)}"
        }



@tool
def search_raw_knowledge(query: str, limit: int = 5) -> dict:
    """
    Search raw document chunks (unverified knowledge).

    Use for exploratory lookups only — NOT for final production answers.
    Use retrieve_expert_knowledge() for verified responses.

    Args:
        query: Search term or question.
        limit: Max chunks to return (default 5, max 20).

    Returns:
        Plain dict with: found, count, chunks (list of dicts), message.
    """
    try:
        limit = max(1, min(limit, 20))
        query_vector = _embedder.get_embedding(query)
        results = _db.semantic_search(query_vector, limit=limit)

        if not results:
            return {
                "found": False,
                "count": 0,
                "chunks": [],
                "message": "No matching document chunks found."
            }

        return {
            "found": True,
            "count": len(results),
            "chunks": [
                {
                    "content":     r.get("content"),
                    "source_path": r.get("source_path"),
                    "similarity":  round(r.get("similarity", 0), 4),
                    "metadata":    r.get("metadata", {})
                }
                for r in results
            ],
            "message": f"Found {len(results)} relevant chunk(s) from raw documents."
        }

    except Exception as e:
        return {
            "found": False,
            "count": 0,
            "chunks": [],
            "message": f"Search error: {str(e)}"
        }
