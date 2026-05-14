"""
routes.py — Skill Execution API Endpoint
==========================================
Uses the unified skill_router for auto-routed execution.
NO if/elif chains — all skills are discovered and routed automatically.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.skills.schemas.base import SkillRequest, SkillResponse
from app.skills.middleware.validation import ValidationGateway
from app.skills.middleware.hooks import StateTracker
from app.skills.database.session import get_db

router = APIRouter()

@router.post("/execute/{skill_name}", response_model=SkillResponse)
async def execute_skill(skill_name: str, request: SkillRequest, db: Session = Depends(get_db)):
    """
    Endpoint for the LLM to trigger a skill.
    The request is validated against strict Pydantic schemas and state is logged.
    Execution is routed automatically via skill_router — no manual mapping needed.
    """
    # 1. Basic sanity check
    if skill_name != request.skill_name:
        raise HTTPException(status_code=400, detail="Path parameter skill_name does not match body skill_name")
    
    # 2. Validation & Authorization Gateway
    ValidationGateway.authorize_request(db, request)
    validated_payload = ValidationGateway.validate_request(request)
    
    # 3. Log Execution Start (State Engine)
    log_entry = StateTracker.log_execution_start(db, request)
    
    # 4. Auto-Routed Execution (NO if/elif chain)
    try:
        from app.skills.functional.skill_router import execute_skill as route_skill

        payload_dict = validated_payload.model_dump()
        result = route_skill(skill_name, payload_dict)
        
        # 5. Log Success
        StateTracker.log_execution_success(db, str(log_entry.id), result)
        
        return SkillResponse(
            status="SUCCESS",
            data=result,
            error_message=None,
            state_reference=UUID(str(log_entry.id))
        )
        
    except Exception as e:
        # 5. Log Failure (HITL Trigger)
        StateTracker.log_execution_failure(db, str(log_entry.id), str(e))
        
        return SkillResponse(
            status="FAILED",
            data=None,
            error_message=str(e),
            state_reference=UUID(str(log_entry.id))
        )
