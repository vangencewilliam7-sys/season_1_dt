from fastapi import APIRouter, HTTPException
from ..services.embeddings import EmbeddingService
from ..services.supabase_client import SupabaseService
from ..services.bypass import BypassService

router = APIRouter()

@router.post("/query/search")
async def semantic_search(query: str, limit: int = 5):
    # (previous implementation)
    embedder = EmbeddingService()
    db = SupabaseService()
    query_vector = embedder.get_embedding(query)
    results = db.semantic_search(query_vector, limit=limit)
    return {"query": query, "results": results}

@router.post("/query")
async def query_twin(prompt: str):
    bypass = BypassService()
    embedder = EmbeddingService()
    db = SupabaseService()
    
    # 1. Emergency Bypass
    if bypass.check_risk(prompt):
        return {
            "status": "emergency_bypass",
            "answer": "I have detected that this may be an emergency. I am routing you immediately to a human doctor.",
            "confidence": 1.0
        }
        
    # 2. High-Purity Vector Search in Expert DNA Vault
    try:
        query_vector = embedder.get_embedding(prompt)
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
        
        # 3. Confidence-Integrated Routing
        if confidence >= 0.90:
            return {
                "status": "autonomous",
                "answer": top_match["expert_decision"],
                "reasoning": top_match.get("reasoning", "Grounded in Expert DNA"),
                "confidence": confidence
            }
        elif confidence >= 0.75:
            # High similarity but not exact - draft for review
            return {
                "status": "human_in_the_loop",
                "answer": "I have an expert-derived recommendation, but I'm requesting final verification from our team to be 100% sure.",
                "draft": top_match["expert_decision"],
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
