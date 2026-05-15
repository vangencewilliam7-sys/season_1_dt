from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..graph.chat_pipeline import create_chat_pipeline
from ..models.chat_state import ChatState
from ..services.pii_scrubber import PIIScrubber
from ..services.bypass import BypassService
from ..adapters import get_adapter, VALID_DOMAINS, VALID_ROLES
import time
import datetime


router = APIRouter()

class ChatRequest(BaseModel):
    expert_id:  str
    message:    str
    session_id: str
    domain:     str  # e.g. "healthcare"
    role:       str  # e.g. "doctor"

@router.post("/chat/message")
async def chat_message(req: ChatRequest):
    """
    Domain-aware chat endpoint. Incorporates Pre-Graph Gatekeeper checks via BypassService,
    injects core metadata tokens, and monitors real-time validation and triage metrics.
    """
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
                "🚨 **PRE-GRAPH GATEKEEPER ESCALATION**\n\n"
                "Critical medical emergency or severe acute risk identified at API ingress boundary.\n\n"
                "**Immediate Action Required:**\n"
                "Please call standard emergency services (911) or proceed directly to your nearest emergency room. "
                "Automated agentic inference has been bypassed to ensure absolute patient safety."
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
