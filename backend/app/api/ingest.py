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
    # Use absolute path derived from __file__ — never hardcode a drive letter
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "uploads")
    upload_dir = os.path.normpath(upload_dir)
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Trigger LangGraph Pipeline — pass file_path via state so the ingestion node doesn't hardcode
    import asyncio
    
    pipeline = create_pipeline()
    initial_state = GraphState(document_id=file_id, source_path=file_path)
    
    try:
        # Run synchronous pipeline.invoke in a threadpool so it doesn't block FastAPI
        # Increased timeout to 5 minutes (300 seconds) because heavy OpenAI processing takes time
        result = await asyncio.wait_for(
            asyncio.to_thread(
                pipeline.invoke, 
                initial_state, 
                {"configurable": {"thread_id": file_id}}
            ),
            timeout=300.0
        )
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

@router.get("/state/{document_id}")
async def get_pipeline_state(document_id: str):
    """Fetches the current suspended state of the LangGraph pipeline for a specific document."""
    from ..graph.pipeline import create_pipeline
    pipeline = create_pipeline()
    
    try:
        # Fetch the state using the checkpointer by passing the thread_id
        state = pipeline.get_state({"configurable": {"thread_id": document_id}})
        if not state or not state.values:
            raise HTTPException(status_code=404, detail="State not found for this document.")
            
        return state.values
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resolve")
async def resolve_scenario(document_id: str, scenario_id: str, audio: UploadFile = File(...)):
    # 1. Save audio to a temp file (next to the running script, no hardcoded paths)
    temp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"temp_audio_{scenario_id}.wav")
    with open(temp_path, "wb") as f:
        f.write(await audio.read())
        
    # 2. Transcribe locally using Faster-Whisper
    from ..services.stt import STTService
    stt = STTService()
    transcript = stt.transcribe_audio(temp_path)
    
    # 3. Clean up temp file
    os.remove(temp_path)
    
    # 4. Return transcript to the UI — graph resumption is handled via POST /commit
    return {
        "status": "transcribed",
        "document_id": document_id,
        "scenario_id": scenario_id,
        "transcript": transcript
    }
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
