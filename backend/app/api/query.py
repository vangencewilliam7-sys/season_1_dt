from fastapi import APIRouter, HTTPException
from ..services.embeddings import EmbeddingService
from ..services.supabase_client import SupabaseService
from ..services.bypass import BypassService
from ..services.guardrail_service import GuardrailService
from ..services.pii_scrubber import PIIScrubber

router = APIRouter()

@router.post("/query/search")
async def semantic_search(query: str, limit: int = 5):
    # (previous implementation)
    scrubber = PIIScrubber()
    clean_query = scrubber.scrub(query)
    embedder = EmbeddingService()
    db = SupabaseService()
    query_vector = embedder.get_embedding(clean_query)
    results = scrubber.restore_object(db.semantic_search(query_vector, limit=limit))
    return {"query": query, "results": results}

@router.post("/query")
async def query_twin(prompt: str):
    scrubber = PIIScrubber()
    clean_prompt = scrubber.scrub(prompt)
    bypass = BypassService()
    embedder = EmbeddingService()
    db = SupabaseService()
    
    # 1. Emergency Bypass
    if bypass.check_risk(clean_prompt):
        return {
            "status": "emergency_bypass",
            "answer": "I have detected that this may be an emergency. I am routing you immediately to a human doctor.",
            "confidence": 1.0
        }
        
    # 2. High-Purity Vector Search in Expert DNA Vault
    try:
        query_vector = embedder.get_embedding(clean_prompt)
        # We search ONLY the expert-verified logic vault for production answers
        results = db.expert_vault_search(query_vector, limit=1)
        
        if not results:
            return {
                "status": "uncertain", 
                "answer": "I don't have human-verified guidance on this specific query yet. I've routed this to our expert desk for review.", 
                "confidence": 0
            }
            
        top_match = results[0]
        confidence = top_match.get("similarity", 0)
        
        # 3. Confidence-Integrated Routing + Guardrail
        if confidence >= 0.85: # Slightly lower threshold but backed by Guardrail
            guard = GuardrailService()
            is_covered = guard.verify_coverage(clean_prompt, top_match["expert_decision"])
            
            if is_covered:
                return {
                    "status": "autonomous",
                    "answer": scrubber.restore(top_match["expert_decision"]),
                    "reasoning": scrubber.restore(top_match.get("reasoning", "Grounded in Expert DNA")),
                    "confidence": confidence
                }
            else:
                return {
                    "status": "out_of_bounds",
                    "answer": "I have identified related knowledge, but it does not specifically cover your query. I have flagged this gap for the doctor to resolve.",
                    "confidence": confidence,
                    "reasoning": "Guardrail detected lack of explicit entailment."
                }
        elif confidence >= 0.70:
            # High similarity but not exact - draft for review
            return {
                "status": "human_in_the_loop",
                "answer": "I have an expert-derived recommendation, but I'm requesting final verification from our team to be 100% sure.",
                "draft": scrubber.restore(top_match["expert_decision"]),
                "confidence": confidence
            }
        else:
            return {
                "status": "uncertain",
                "answer": "I'm not confident enough to answer this yet. Paging an expert...",
                "confidence": confidence
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
