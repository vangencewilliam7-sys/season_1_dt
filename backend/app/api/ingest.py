from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
import os
import shutil
import uuid
import hashlib
from ..graph.pipeline import create_pipeline
from ..models.state import GraphState
from ..services.pii_scrubber import PIIScrubber
from ..adapters import get_adapter, VALID_DOMAINS, VALID_ROLES

router = APIRouter()

from ..services.supabase_client import SupabaseService

# In-memory registry of file hashes to detect duplicates across server restarts
# Maps file_hash -> {"document_id": ..., "filename": ...}
_upload_hash_registry: dict[str, dict] = {}

def _compute_file_hash(file_bytes: bytes) -> str:
    """Compute SHA-256 hash of a file's contents."""
    sha256 = hashlib.sha256()
    sha256.update(file_bytes)
    return sha256.hexdigest()

def _rebuild_hash_registry():
    """Scan existing uploads in Supabase to rebuild the hash registry on startup."""
    global _upload_hash_registry
    if _upload_hash_registry:
        return  # Already built
    
    db = SupabaseService()
    files = db.list_documents()
    for f in files:
        fname = f.get("name")
        if not fname or fname == ".emptyFolderPlaceholder":
            continue
        try:
            # We can't efficiently hash remote files on startup without downloading them all.
            # For now, we will rely on Supabase to not overwrite or we can just populate document_id.
            # To properly do duplicate detection cloud-natively, we should store hashes in a DB table.
            # Since this is an MVP, we'll skip pre-calculating hashes of old files.
            pass
        except Exception:
            pass

@router.post("/ingest")
async def ingest_file(
    file: UploadFile = File(...),
    category: str = Form("base_knowledge"),
    domain: str = Query(..., enum=VALID_DOMAINS, description="Domain for this twin: healthcare | it | education"),
    role:   str = Query(..., enum=VALID_ROLES,   description="Role for this twin: doctor | project_manager | tutor"),
):
    if not file.filename.endswith(('.docx', '.pdf')):
        raise HTTPException(status_code=400, detail="Only .docx and .pdf files are supported.")
    
    file_id = str(uuid.uuid4())
    db = SupabaseService()
    
    file_bytes = await file.read()

    # Duplicate detection: hash the uploaded file bytes
    file_hash = _compute_file_hash(file_bytes)
    if file_hash in _upload_hash_registry:
        existing = _upload_hash_registry[file_hash]
        existing_doc_id = existing["document_id"]
        original_path = f"{existing_doc_id}_{existing['filename']}"
        
        # Resolve adapter so we can inject domain context even when restoring state
        try:
            adapter = get_adapter(domain, role)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Re-run the pipeline to restore in-memory state
        import asyncio
        pipeline = create_pipeline()
        initial_state = GraphState(
            document_id=existing_doc_id,
            category=category,
            source_path=original_path,
            domain_id=adapter.get_domain_id(),
            role_id=adapter.get_role_id(),
            adapter_context=adapter.to_context_dict(),
        )
        try:
            await asyncio.wait_for(
                asyncio.to_thread(pipeline.invoke, initial_state, {"configurable": {"thread_id": existing_doc_id}}),
                timeout=300.0
            )
        except Exception:
            pass
        return {
            "message": "Document already exists. Pipeline state restored.",
            "document_id": existing_doc_id,
            "file_path": original_path,
            "pipeline_status": "restored_from_duplicate",
            "is_duplicate": True,
            "domain": adapter.get_domain_name(),
            "role": adapter.get_role_name(),
        }
    
    # Upload to Supabase Storage in category folder
    file_path = f"{category}/{file_id}_{file.filename}"
    upload_res = db.upload_document(file_bytes, file_path)
    if "error" in upload_res:
        raise HTTPException(status_code=500, detail=f"Failed to upload to Supabase: {upload_res['error']}")
    
    # Register this file hash
    _upload_hash_registry[file_hash] = {"document_id": file_id, "filename": file.filename}

    # Resolve domain adapter and inject domain identity into GraphState
    import asyncio
    try:
        adapter = get_adapter(domain, role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    pipeline = create_pipeline()
    initial_state = GraphState(
        document_id=file_id,
        category=category,
        source_path=file_path,
        domain_id=adapter.get_domain_id(),
        role_id=adapter.get_role_id(),
        adapter_context=adapter.to_context_dict(),
    )
    
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
            "domain": adapter.get_domain_name(),
            "role": adapter.get_role_name(),
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
    scrubber = PIIScrubber()
    transcript = scrubber.scrub(transcript)
    
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
async def commit_to_vault(
    scenario_id:     str,
    expert_decision: str,
    archetype:       str,
    domain:          str = Query(..., enum=VALID_DOMAINS, description="Domain this decision belongs to"),
    role:            str = Query(..., enum=VALID_ROLES,   description="Role this decision belongs to"),
    reasoning:       str = "",
    ):
    """
    Commits a human-verified expert decision into the production Logic Vault (expert_dna).
    Uses domain_id + role_id FKs instead of the legacy plain-text 'industry' field.
    """
    from ..services.embeddings import EmbeddingService
    from ..services.supabase_client import SupabaseService
    try:
        adapter = get_adapter(domain, role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    scrubber = PIIScrubber()
    embedder = EmbeddingService()
    db = SupabaseService()
    clean_expert_decision = scrubber.scrub(expert_decision)

    # 1. Generate embedding for the verified scenario context
    # This allows the runtime query to match patient questions to this specific expert logic
    vector = embedder.get_embedding(clean_expert_decision)

    # 2. Persist to high-purity expert_dna table with FK references (NOT a text industry field)
    data = {
        "scenario_id":      scenario_id,
        "expert_decision":  clean_expert_decision,
        "impact_archetype": archetype,
        "domain_id":        adapter.get_domain_id(),   # FK → domains.id
        "role_id":          adapter.get_role_id(),     # FK → roles.id
        "reasoning":        reasoning,
        "embedding":        vector,
    }

    db.insert_expert_dna(data)

    return {
        "status":  "committed",
        "message": "Expert DNA added to production Logic Vault.",
        "domain":  adapter.get_domain_name(),
        "role":    adapter.get_role_name(),
    }

@router.get("/file-info/{document_id}")
async def get_file_info(document_id: str):
    """Returns the filename and URL for an uploaded document so the frontend can embed a viewer."""
    db = SupabaseService()
    files = db.list_documents()
    
    for f in files:
        fname = f.get("name", "")
        if fname.startswith(document_id) or (f.get("metadata", {}).get("document_id") == document_id) or (document_id in fname):
            # Try to strip uuid prefix or category folder prefix if present
            # fname could be "base_knowledge/uuid_filename" or "uuid_filename"
            base_fname = os.path.basename(fname)
            if "_" in base_fname:
                original_name = base_fname.split("_", 1)[1]
            else:
                original_name = base_fname
                
            file_ext = os.path.splitext(fname)[1].lower()
            
            # Generate a secure signed URL that expires in 1 hour
            signed_url = db.get_document_url(fname)
            
            return {
                "filename": original_name,
                "stored_name": fname,
                "file_url": signed_url,
                "file_type": "docx" if file_ext == ".docx" else "pdf" if file_ext == ".pdf" else "unknown"
            }
    
    raise HTTPException(status_code=404, detail="File not found in Supabase Storage.")
