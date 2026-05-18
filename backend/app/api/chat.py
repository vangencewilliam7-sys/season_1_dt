from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..graph.chat_pipeline import create_chat_pipeline
from ..models.chat_state import ChatState
from ..services.pii_scrubber import PIIScrubber
from ..services.bypass import BypassService
from ..adapters import get_adapter, VALID_DOMAINS, VALID_ROLES
from ..services.implicit_ingester import ImplicitIngester
from ..services.supabase_client import SupabaseService
import time
import datetime

router = APIRouter()

class ChatRequest(BaseModel):
    expert_id:  str
    message:    str
    session_id: str
    domain:     str  # e.g. "healthcare"
    role:       str  # e.g. "doctor"

class OverrideRequest(BaseModel):
    session_id: str
    active: bool

class ExpertMessageRequest(BaseModel):
    expert_id: str
    message: str
    session_id: str
    domain: str
    role: str

@router.post("/chat/message")
async def chat_message(req: ChatRequest):
    """
    Domain-aware chat endpoint. Incorporates Pre-Graph Gatekeeper checks via BypassService,
    injects core metadata tokens, and monitors real-time validation and triage metrics.
    """
    db = SupabaseService()
    
    # 0. Check for Human Intervention Override
    status = db.get_pipeline_status(req.session_id)
    if status == 'human_intervention':
        return {
            "response": "The Expert is currently typing directly...",
            "confidence": 1.0,
            "persona_mode": "offline",
            "sources": [],
            "rationale": "Twin is silenced. Waiting for Expert direct message.",
            "latency_ms": 0,
            "domain": req.domain,
            "role": req.role,
            "intent_type": "knowledge",
            "skill_result": None,
            "skill_status": "DISABLED",
            "detected_skill": "",
            "extracted_params": {},
            "low_data_mode": False,
            "missing_metrics": [],
            "accumulated_evidence": {},
            "likelihood_score": "",
            "is_valid": True,
            "triage_level": "GREEN_ZONE"
        }

    scrubber = PIIScrubber()
    scrubbed_msg = scrubber.scrub(req.message)
    
    # 1. Resolve domain adapter
    try:
        adapter = get_adapter(req.domain, req.role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. Pre-Graph Gatekeeper Bypass Check
    bypass_service = BypassService()
    if bypass_service.check_risk(scrubbed_msg):
        # Escalate immediately without instantiating or executing the LangGraph pipeline
        return {
            "response": (
                "🚨 **Please Seek Immediate Medical Attention**\n\n"
                "I am extremely concerned by what you are describing. These symptoms indicate a critical medical emergency that cannot be safely evaluated online.\n\n"
                "**Please take this seriously and act immediately:**\n"
                "Call your local emergency services (911) right now, or proceed immediately to the nearest emergency room. Do not wait for an appointment."
            ),
            "confidence": 1.0,
            "persona_mode": "deputy",
            "sources": [],
            "rationale": "Ingress bypass: Query triggered absolute API risk threshold boundaries.",
            "latency_ms": 15,
            "domain": adapter.get_domain_name(),
            "role": adapter.get_role_name(),
            "intent_type": "emergency_escalation",
            "skill_result": None,
            "skill_status": "",
            "detected_skill": "",
            "extracted_params": {},
            "low_data_mode": False,
            "missing_metrics": [],
            "accumulated_evidence": {},
            "likelihood_score": "",
            "is_valid": True,
            "triage_level": "RED_ZONE"
        }

    pipeline = create_chat_pipeline()
    initial_state = ChatState(
        expert_id=req.expert_id,
        session_id=req.session_id,
        query=scrubbed_msg,
        domain_id=adapter.get_domain_id(),
        role_id=adapter.get_role_id(),
        adapter_context={
            **adapter.to_context_dict(),
            "system_prompt": adapter.get_system_prompt(),
        },
    )

    try:
        import asyncio
        start_time = time.time()

        result_state_dict = await asyncio.to_thread(
            pipeline.invoke,
            initial_state
        )

        if not isinstance(result_state_dict, dict):
            result_state_dict = {}

        latency = int((time.time() - start_time) * 1000)
        
        # Extract from state dict returned by LangGraph
        response_text = scrubber.restore(result_state_dict.get("response", ""))
        confidence = result_state_dict.get("confidence", 0.0)
        persona_mode = result_state_dict.get("persona_mode", "offline")
        rationale = scrubber.restore(result_state_dict.get("rationale", ""))
        sources = [f"Logic Vault ID: {r.get('scenario_id', 'Unknown')}" for r in result_state_dict.get("retrieved_cases", [])]
        
        # SKILL FIELDS
        intent_type = result_state_dict.get("intent_type", "knowledge")
        skill_result = result_state_dict.get("skill_result")
        skill_status = result_state_dict.get("skill_status", "")
        detected_skill = result_state_dict.get("detected_skill", "")
        extracted_params = result_state_dict.get("extracted_params", {})

        # PROXY GATHERING FIELDS
        low_data_mode = result_state_dict.get("low_data_mode", False)
        missing_metrics = result_state_dict.get("missing_metrics", [])
        accumulated_evidence = result_state_dict.get("accumulated_evidence", {})
        likelihood_score = result_state_dict.get("likelihood_score", "")
        
        # VALIDATION & TRIAGE FIELDS
        is_valid = result_state_dict.get("is_valid", True)
        triage_level = result_state_dict.get("triage_level", "GREEN_ZONE")

        return {
            "response":     response_text,
            "confidence":   confidence,
            "persona_mode": persona_mode,
            "sources":      sources,
            "rationale":    rationale,
            "latency_ms":   latency,
            "domain":       adapter.get_domain_name(),
            "role":         adapter.get_role_name(),
            "intent_type":  intent_type,
            "skill_result": skill_result,
            "skill_status": skill_status,
            "detected_skill": detected_skill,
            "extracted_params": extracted_params,
            "low_data_mode": low_data_mode,
            "missing_metrics": missing_metrics,
            "accumulated_evidence": accumulated_evidence,
            "likelihood_score": likelihood_score,
            "is_valid":     is_valid,
            "triage_level": triage_level
        }
    except Exception as e:
        import traceback
        with open("error_log.txt", "a") as f:
            f.write(f"\n--- ERROR at {datetime.datetime.now()} ---\n")
            f.write(traceback.format_exc())
        print(f"Chat Engine Error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/override")
async def toggle_override(req: OverrideRequest):
    """
    Toggles the human intervention override state for a session.
    """
    db = SupabaseService()
    status = "human_intervention" if req.active else "in_progress"
    db.update_pipeline_status(req.session_id, status)
    return {"status": status, "session_id": req.session_id}

@router.post("/chat/expert-message")
async def expert_message(req: ExpertMessageRequest, background_tasks: BackgroundTasks):
    """
    Endpoint for human experts to send direct messages to the user.
    Bypasses the LangGraph Twin logic.
    Also triggers implicit ingestion to learn from the expert's message.
    """
    db = SupabaseService()
    
    # In a real system, we'd broadcast this to the user via WebSockets.
    # For now, we simulate logging it directly to the chat history.
    db.insert_chat_audit_log({
        "session_id": req.session_id,
        "user_query": "", # It's a direct message, no user query
        "final_response": req.message,
        "sender": "human_expert", # Requires the new column added in 10_human_override.sql
        "domain_id": req.domain,
        "role_id": req.role,
        "rationale_used": "Direct Expert Override",
        "confidence_score": 1.0,
        "latency_ms": 0
    })

    # Trigger implicit ingestion in the background
    ingester = ImplicitIngester()
    
    # Wait, we need domain_id and role_id as UUIDs ideally. Since the API gets strings,
    # let's resolve them using adapter.
    try:
        adapter = get_adapter(req.domain, req.role)
        domain_id = adapter.get_domain_id()
        role_id = adapter.get_role_id()
    except Exception as e:
        domain_id = req.domain
        role_id = req.role

    # Background task to run ingestion
    async def run_ingestion():
        await ingester.ingest_expert_interaction(
            session_id=req.session_id,
            expert_message=req.message,
            domain_id=domain_id,
            role_id=role_id
        )

    background_tasks.add_task(run_ingestion)
    
    return {
        "status": "sent",
        "message": req.message,
        "session_id": req.session_id
    }

@router.get("/chat/history")
async def chat_history(session_id: str):
    """
    Retrieves chronological chat history for a given session.
    Also returns the active override status of the session.
    """
    db = SupabaseService()
    status = db.get_pipeline_status(session_id)
    
    if not db.client:
        return {"status": status, "messages": []}
        
    try:
        res = db.client.table("chat_audit_logs")\
            .select("*")\
            .eq("session_id", session_id)\
            .order("created_at", desc=False)\
            .execute()
            
        messages: list[Dict[str, Any]] = []
        if res.data:
            for log in res.data:
                if not isinstance(log, dict):
                    continue
                # 1. If there's a user query, add the user bubble
                user_query = log.get("user_query")
                if isinstance(user_query, str) and user_query.strip():
                    messages.append({
                        "role": "user",
                        "content": user_query
                    })
                # 2. If there's a response, add the assistant/expert bubble
                final_response = log.get("final_response")
                if isinstance(final_response, str) and final_response.strip():
                    sender_raw = log.get("sender")
                    sender = sender_raw if isinstance(sender_raw, str) else "twin"
                    
                    conf_raw = log.get("confidence")
                    if isinstance(conf_raw, (int, float, str)):
                        try:
                            confidence = float(conf_raw)
                        except ValueError:
                            confidence = 0.0
                    else:
                        confidence = 0.0
                        
                    rat_used = log.get("rationale_used")
                    rat = log.get("rationale")
                    rationale = rat_used if isinstance(rat_used, str) and rat_used else (rat if isinstance(rat, str) else "")
                    
                    created_raw = log.get("created_at")
                    created_at = created_raw if isinstance(created_raw, str) else ""

                    messages.append({
                        "role": "assistant",
                        "content": final_response,
                        "sender": sender,
                        "confidence": confidence,
                        "rationale": rationale,
                        "created_at": created_at
                    })
        return {"status": status, "messages": messages}
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        return {"status": status, "messages": []}
