from fastapi import APIRouter
from ..services.supabase_client import SupabaseService

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats():
    db = SupabaseService()
    
    # These methods should be added to SupabaseService
    doc_count = db.get_count("document_chunks")
    case_count = db.get_count("expert_dna") # The vault table
    manifest_count = db.get_count("persona_manifests")
    gap_count = db.get_count("decision_gaps")
    
    return {
        "documentsIngested": doc_count,
        "masterCases": case_count,
        "personaManifests": manifest_count,
        "knowledgeGapsFlagged": gap_count
    }
