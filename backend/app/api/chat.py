from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..graph.chat_pipeline import create_chat_pipeline
from ..models.chat_state import ChatState
from ..services.pii_scrubber import PIIScrubber
from ..adapters import get_adapter, VALID_DOMAINS, VALID_ROLES
import time

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
    Domain-aware chat endpoint. The adapter injects the correct system prompt
    and confidence threshold for the target twin before the chat pipeline runs.
    """
    scrubber = PIIScrubber()
    # 1. Resolve domain adapter
    try:
        adapter = get_adapter(req.domain, req.role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    pipeline = create_chat_pipeline()
    initial_state = ChatState(
        expert_id=req.expert_id,
        session_id=req.session_id,
        query=scrubber.scrub(req.message),
        domain_id=adapter.get_domain_id(),
        role_id=adapter.get_role_id(),
        adapter_context={
            **adapter.to_context_dict(),
            "system_prompt": adapter.get_system_prompt(),  # Full prompt included for chat nodes
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
        
        # NEW SKILL FIELDS
        intent_type = result_state_dict.get("intent_type", "knowledge")
        skill_result = result_state_dict.get("skill_result")
        skill_status = result_state_dict.get("skill_status", "")
        detected_skill = result_state_dict.get("detected_skill", "")
        extracted_params = result_state_dict.get("extracted_params", {})

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
            "extracted_params": extracted_params
        }
    except Exception as e:
        print(f"Chat Engine Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
