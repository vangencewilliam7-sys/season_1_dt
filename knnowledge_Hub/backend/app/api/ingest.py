from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
import uuid
from ..graph.pipeline import create_pipeline
from ..models.state import GraphState

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    if not file.filename.endswith(('.docx', '.pdf')):
        raise HTTPException(status_code=400, detail="Only .docx and .pdf files are supported.")
    
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Trigger LangGraph Pipeline
    app = create_pipeline()
    initial_state = GraphState(document_id=file_id)
    # We pass the file_path in metadata or state if needed
    # For now, we'll assume the ingestion node knows where files live or we add it to state
    # Let's add source_path to state in next iteration for clarity
    
    # Run the graph
    try:
        # We run the graph. It will process ingestion, divergence, and SLM audit, 
        # then pause at the Socratic (HITL) node.
        result = app.invoke(initial_state, config={"configurable": {"thread_id": file_id}})
        return {
            "message": "Ingestion started and processed up to HITL breakpoint",
            "document_id": file_id,
            "file_path": file_path,
            "pipeline_status": "paused_at_socratic_node"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/context")
async def get_industry_context():
    from ..services.context_manager import ContextManager
    cm = ContextManager()
    return cm.get_context()

@router.post("/resolve")
async def resolve_scenario(document_id: str, scenario_id: str, audio: UploadFile = File(...)):
    # 1. Save audio to temp file
    temp_path = f"temp_audio_{scenario_id}.wav"
    with open(temp_path, "wb") as f:
        f.write(await audio.read())
        
    # 2. Transcribe locally using Faster-Whisper
    from ..services.stt import STTService
    stt = STTService()
    transcript = stt.transcribe_audio(temp_path)
    
    # 3. Clean up
    os.remove(temp_path)
    
    # 4. Resume the Graph for this document
    # For now, we simulate the logic parsing result so the UI can show the audit gate
    # In production, this would be the actual state update from the Parser node.
@router.post("/commit")
async def commit_to_vault(scenario_id: str, expert_decision: str, archetype: str, industry: str = "fertility"):
    """Moves verified logic from the pipeline into the production Logic Vault."""
    from ..services.embeddings import EmbeddingService
    from ..services.supabase_client import SupabaseService
    
    embedder = EmbeddingService()
    db = SupabaseService()
    
    # 1. Generate embedding for the verified scenario context
    # This allows the runtime query to match patient questions to this specific expert logic
    vector = embedder.get_embedding(expert_decision)
    
    # 2. Persist to high-purity expert_dna table
    data = {
        "scenario_id": scenario_id,
        "expert_decision": expert_decision,
        "impact_archetype": archetype,
        "industry": industry,
        "embedding": vector
    }
    
    db.insert_expert_dna(data)
    
    return {"status": "committed", "message": "Expert DNA added to production Logic Vault."}
