"""
runtime/api/extraction.py

Extraction API endpoints.

POST /extract/start   — Start a new persona extraction run
GET  /extract/{id}/status — Check progress of a running extraction
GET  /extract/{id}/manifest — Retrieve the completed PersonaManifest
"""

import os
import json
import logging
import uuid
import shutil
from typing import Optional, List

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from core.graph import build_extraction_graph, create_initial_state
from langgraph.checkpoint.memory import MemorySaver

import runtime.db as db
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/extract", tags=["Extraction"])

# ── Request / Response models ─────────────────────────────────────────────────

class ExtractionRequest(BaseModel):
    expert_id: str
    expert_name: Optional[str] = None
    expert_role: Optional[str] = None
    reader_type: str = "filesystem"          # "filesystem" | "api"
    reader_config: dict = {}                 # e.g. {"base_dir": "d:/data"}


class ExtractionJob(BaseModel):
    job_id: str
    expert_id: str
    status: str                              # "pending" | "running" | "complete" | "failed"
    current_node: Optional[str] = None
    error: Optional[str] = None
    manifest_available: bool = False


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/{expert_id}/upload")
async def upload_expert_documents(
    expert_id: str,
    folder: str = Form(...), # "knowledge_hub" or "master_cases"
    files: List[UploadFile] = File(...)
):
    """Upload documents to the expert's data directory."""
    if folder not in ["knowledge_hub", "master_cases"]:
        raise HTTPException(status_code=400, detail="Invalid folder type. Must be knowledge_hub or master_cases")

    target_dir = os.path.join("data", expert_id, folder)
    os.makedirs(target_dir, exist_ok=True)

    uploaded_files = []
    for file in files:
        file_path = os.path.join(target_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded_files.append(file.filename)

    logger.info(f"[ExtractionAPI] Uploaded {len(uploaded_files)} files to {expert_id}/{folder}")
    return {"message": "Success", "files": uploaded_files}


@router.post("/start", response_model=ExtractionJob)
async def start_extraction(
    request: ExtractionRequest,
    background_tasks: BackgroundTasks,
):
    """
    Start a new persona extraction run for the given expert.
    The extraction runs asynchronously — poll /extract/{job_id}/status to track.
    """
    job_id = str(uuid.uuid4())
    
    # Ensure expert exists in DB
    db.create_expert(
        expert_id=request.expert_id, 
        name=request.expert_name or "Unknown Expert", 
        role=request.expert_role or "Unknown Role", 
        domain=settings.domain_adapter
    )
    
    # Create the session in DB
    db.create_extraction_session(job_id, request.expert_id)

    background_tasks.add_task(
        _run_extraction,
        job_id=job_id,
        request=request,
    )

    logger.info(f"[ExtractionAPI] Job {job_id} queued for expert: {request.expert_id}")

    return ExtractionJob(
        job_id=job_id,
        expert_id=request.expert_id,
        status="pending",
    )


@router.get("/{job_id}/status", response_model=ExtractionJob)
async def get_extraction_status(job_id: str):
    """Poll the status of an ongoing or completed extraction job."""
    session = db.get_session(job_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return ExtractionJob(
        job_id=job_id,
        expert_id=session["expert_id"],
        status=session["status"],
        current_node=session.get("current_node"),
        error=session.get("error"),
        manifest_available=(session["status"] == "complete"),
    )


@router.get("/{job_id}/manifest")
async def get_manifest(job_id: str):
    """
    Retrieve the completed PersonaManifest for a finished extraction job.
    Only available when status = 'complete'.
    """
    session = db.get_session(job_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    if session["status"] != "complete":
        raise HTTPException(
            status_code=400,
            detail=f"Manifest not ready. Current status: {session['status']}"
        )
        
    with db.get_connection() as conn:
        with conn.cursor(cursor_factory=db.psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT raw_manifest_json FROM persona_manifests WHERE session_id = %s", (job_id,))
            manifest_row = cur.fetchone()
            if not manifest_row:
                raise HTTPException(status_code=404, detail="Manifest data not found in DB")
            
            return {
                "manifest": manifest_row["raw_manifest_json"],
                "shadow_approved": False,
            }


class ExpertAnswer(BaseModel):
    question_index: int
    answer: str
    confidence: str
    is_outside_scope: Optional[bool] = False

class AnswersRequest(BaseModel):
    answers: List[ExpertAnswer]


@router.get("/{job_id}/questions")
async def get_questions(job_id: str):
    """Retrieve the generated questions for the expert to answer."""
    session = db.get_session(job_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    if session["status"] != "awaiting_answers":
        raise HTTPException(
            status_code=400,
            detail=f"Questions not ready. Current status: {session['status']}"
        )
    
    with db.get_connection() as conn:
        with conn.cursor(cursor_factory=db.psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT question_text FROM scenarios WHERE session_id = %s ORDER BY created_at ASC", (job_id,))
            rows = cur.fetchall()
            questions = [row["question_text"] for row in rows]
            return {
                "questions": questions
            }


@router.post("/{job_id}/answers")
async def submit_answers(job_id: str, request: AnswersRequest, background_tasks: BackgroundTasks):
    """Submit manual answers and resume the extraction pipeline."""
    session = db.get_session(job_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    if session["status"] != "awaiting_answers":
        raise HTTPException(status_code=400, detail="Job is not waiting for answers.")

    db.update_session_status(job_id, "processing_answers", "answer_processor")
    
    # Save answers to the database
    answers_dicts = [a.model_dump() for a in request.answers]
    db.save_answers(job_id, session["expert_id"], answers_dicts)

    background_tasks.add_task(
        _resume_extraction,
        job_id=job_id,
        answers=answers_dicts
    )

    return {"status": "processing_answers"}

# Shared memory checkpointer for the demo
memory = MemorySaver()



# ── Background Task ───────────────────────────────────────────────────────────

async def _run_extraction(job_id: str, request: ExtractionRequest):
    """Runs the full extraction pipeline in the background."""
    from runtime.main import get_adapter, get_llm_ingestion, get_llm_journalist, get_reader

    db.update_session_status(job_id, "running", "loading_documents")

    try:
        # Build the reader for this request
        reader = get_reader(request.reader_type, request.reader_config)

        # Load documents from Knowledge Hub + Master Cases
        documents = reader.load(request.expert_id)
        if not documents:
            raise ValueError(f"No documents found for expert: {request.expert_id}")

        logger.info(f"[Job:{job_id}] Loaded {len(documents)} documents")

        # Serialise documents for LangGraph state
        doc_dicts = [doc.to_dict() for doc in documents]

        adapter = get_adapter()
        from core.graph import build_extraction_graph
        graph = build_extraction_graph(
            llm_ingestion=get_llm_ingestion(),
            llm_journalist=get_llm_journalist(),
            adapter=adapter,
        )
        graph.checkpointer = memory

        # Create initial state
        initial_state = create_initial_state(
            expert_id=request.expert_id,
            domain=adapter.get_domain_id(),
            documents=doc_dicts,
            identity_override={
                "name": request.expert_name or "Unknown Expert",
                "role": request.expert_role or "Unknown Role",
            },
        )

        config = {"configurable": {"thread_id": job_id}}

        # Run the pipeline until interrupt
        db.update_session_status(job_id, "running", "ingestion")
        for event in graph.stream(initial_state, config=config):
            pass

        state = graph.get_state(config)
        
        if state.values.get("error"):
            raise ValueError(state.values["error"])

        if state.next:
            # We hit the interrupt
            db.update_session_status(job_id, "awaiting_answers", "awaiting_answers")
            
            # Save the generated questions to the DB
            generated_questions = state.values.get("generated_questions", [])
            db.save_scenarios(job_id, request.expert_id, generated_questions)
            
            logger.info(f"[Job:{job_id}] Pipeline paused. Awaiting answers.")
            return

        # It completed without interrupting (shouldn't happen unless error)
        db.update_session_status(job_id, "complete")
        db.save_persona_manifest(job_id, request.expert_id, state.values.get("final_manifest", {}))

    except Exception as e:
        logger.error(f"[Job:{job_id}] Extraction failed: {e}")
        db.update_session_status(job_id, "failed", None, str(e))

async def _resume_extraction(job_id: str, answers: list):
    """Resumes the graph after expert answers are provided."""
    from runtime.main import get_adapter, get_llm_ingestion, get_llm_journalist

    session = db.get_session(job_id)

    try:
        adapter = get_adapter()
        from core.graph import build_extraction_graph
        graph = build_extraction_graph(
            llm_ingestion=get_llm_ingestion(),
            llm_journalist=get_llm_journalist(),
            adapter=adapter,
        )
        graph.checkpointer = memory

        config = {"configurable": {"thread_id": job_id}}
        
        # Update the state with the answers
        graph.update_state(config, {"expert_answers": answers})

        db.update_session_status(job_id, "processing_answers", "answer_processor")

        # Resume
        for event in graph.stream(None, config=config):
            pass

        state = graph.get_state(config)

        if state.values.get("error"):
            raise ValueError(state.values["error"])

        db.update_session_status(job_id, "complete", None, None)
        
        # Save the final manifest
        manifest = state.values.get("final_manifest", {})
        if manifest:
            db.save_persona_manifest(job_id, session["expert_id"], manifest)
            
        logger.info(f"[Job:{job_id}] Extraction resumed and completed.")

    except Exception as e:
        logger.error(f"[Job:{job_id}] Resume failed: {e}")
        db.update_session_status(job_id, "failed", None, str(e))
