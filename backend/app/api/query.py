from fastapi import APIRouter, HTTPException, Query
from ..services.embeddings import EmbeddingService
from ..services.supabase_client import SupabaseService
from ..services.bypass import BypassService
from ..services.guardrail_service import GuardrailService
from ..services.pii_scrubber import PIIScrubber
from ..adapters import get_adapter, VALID_DOMAINS, VALID_ROLES

router = APIRouter()

@router.post("/query/search")
async def semantic_search(query: str, limit: int = 5):
    """Raw semantic search over document_chunks (unverified knowledge)."""
    scrubber = PIIScrubber()
    clean_query = scrubber.scrub(query)
    embedder = EmbeddingService()
    db = SupabaseService()
    query_vector = embedder.get_embedding(clean_query)
    results = scrubber.restore_object(db.semantic_search(query_vector, limit=limit))
    return {"query": query, "results": results}

@router.post("/query")
async def query_twin(
    prompt: str,
    domain: str = Query(..., enum=VALID_DOMAINS, description="Domain to query: healthcare | it | education"),
    role:   str = Query(..., enum=VALID_ROLES,   description="Role to query: doctor | project_manager | tutor"),
):
    """
    Domain-aware query against the Expert DNA Logic Vault.
    Results are strictly filtered by domain_id and confidence is evaluated
    against the per-domain threshold defined in the adapter.
    """
    # Resolve adapter — raises 400 if domain/role pair is invalid
    try:
        adapter = get_adapter(domain, role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    scrubber = PIIScrubber()
    clean_prompt = scrubber.scrub(prompt)
    bypass = BypassService()
    embedder = EmbeddingService()
    db = SupabaseService()

    # 1. Emergency Bypass (domain-agnostic safety layer)
    if bypass.check_risk(clean_prompt):
        return {
            "status":     "emergency_bypass",
            "answer":     f"I have detected a potential emergency. Routing immediately to a human {adapter.get_fallback_identity()}.",
            "confidence": 1.0,
            "domain":     adapter.get_domain_name(),
            "role":       adapter.get_role_name(),
        }

    # 2. Domain-scoped Vector Search in Expert DNA Vault
    try:
        query_vector = embedder.get_embedding(clean_prompt)
        results = db.expert_vault_search(
            query_vector,
            domain_id=adapter.get_domain_id(),  # FK filter — no cross-domain bleed
            limit=1,
        )

        if not results:
            return {
                "status":     "uncertain",
                "answer":     (
                    f"I don't have human-verified guidance for this query "
                    f"in the {adapter.get_domain_name()} / {adapter.get_role_name()} domain yet. "
                    f"Routing to {adapter.get_fallback_identity()} for review."
                ),
                "confidence": 0,
                "domain":     adapter.get_domain_name(),
                "role":       adapter.get_role_name(),
            }

        top_match = results[0]
        confidence = top_match.get("similarity", 0)
        threshold  = adapter.get_confidence_threshold()

        # 3. Confidence-Integrated Routing + Guardrail
        # Use adapter threshold + offset for autonomous confidence zone
        if confidence >= threshold + 0.15:
            guard = GuardrailService()
            is_covered = guard.verify_coverage(clean_prompt, top_match["expert_decision"])
            
            if is_covered:
                return {
                    "status":     "autonomous",
                    "answer":     scrubber.restore(top_match["expert_decision"]),
                    "reasoning":  scrubber.restore(top_match.get("reasoning", f"Grounded in Expert DNA (archetype: {top_match.get('impact_archetype', 'N/A')})")),
                    "confidence": confidence,
                    "domain":     adapter.get_domain_name(),
                    "role":       adapter.get_role_name(),
                }
            else:
                return {
                    "status":     "out_of_bounds",
                    "answer":     f"I have identified related knowledge, but it does not specifically cover your query. I have flagged this gap for the {adapter.get_fallback_identity()} to resolve.",
                    "confidence": confidence,
                    "reasoning":  "Guardrail detected lack of explicit entailment.",
                    "domain":     adapter.get_domain_name(),
                    "role":       adapter.get_role_name(),
                }
        elif confidence >= threshold:
            # High similarity but not exact - draft for review
            return {
                "status":     "human_in_the_loop",
                "answer":     f"I have an expert-derived recommendation, but I'm requesting final verification from our {adapter.get_fallback_identity()} to be 100% sure.",
                "draft":      scrubber.restore(top_match["expert_decision"]),
                "confidence": confidence,
                "domain":     adapter.get_domain_name(),
                "role":       adapter.get_role_name(),
            }
        else:                                       # Below threshold → fall back
            return {
                "status":     "uncertain",
                "answer":     f"Confidence too low to respond autonomously. Paging {adapter.get_fallback_identity()}...",
                "confidence": confidence,
                "domain":     adapter.get_domain_name(),
                "role":       adapter.get_role_name(),
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

