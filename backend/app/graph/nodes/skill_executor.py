"""
skill_executor.py — Graph Node: Skill Execution
=================================================
Uses the unified skill_router for auto-routed execution.
NO if/elif chains — all skills are discovered and routed automatically.
"""
from app.models.chat_state import ChatState
from app.skills.middleware.validation import ValidationGateway, SKILL_REGISTRY
from app.skills.database.session import SessionLocal
from app.skills.schemas.base import SkillRequest
from app.skills.middleware.hooks import StateTracker


def skill_executor_node(state: ChatState) -> ChatState:
    print(f"--- CHAT: Skill Executor Node ---")
    
    skill_name = state.detected_skill
    params = state.extracted_params
    
    # 1. Check if skill is registered
    if skill_name not in SKILL_REGISTRY:
        state.skill_status = "NOT_REGISTERED"

        # Dynamically list available skills from the registry
        available = list(SKILL_REGISTRY.keys())
        skill_list = "\n".join(f"- {s}" for s in available)

        state.response = (
            f"🔧 I understand you'd like me to perform an action. "
            f"Unfortunately, this action isn't available in my current skill set yet.\n\n"
            f"**Skills I can currently perform:**\n{skill_list}\n\n"
            f"Would you like me to help with any of these instead?"
        )
        return state

    import uuid
    from app.skills.schemas.base import SkillMetadata
    
    try:
        expert_uuid = uuid.UUID(state.expert_id)
    except Exception:
        expert_uuid = uuid.uuid4()
        
    metadata = SkillMetadata(
        workflow_id=uuid.uuid4(),
        expert_id=expert_uuid
    )

    # 2. Build SkillRequest
    request = SkillRequest(
        skill_name=skill_name,
        payload=params,
        metadata=metadata
    )

    db = SessionLocal()
    log_entry = None
    try:
        # 3. Check Guardrails
        ValidationGateway.authorize_request(db, request)
        
        # 4. Validate payload
        validated_payload = ValidationGateway.validate_request(request)
        
        # 5. Log Execution Start
        log_entry = StateTracker.log_execution_start(db, request)
        
        # 6. Auto-Routed Execution (NO if/elif chain)
        from app.skills.functional.skill_router import execute_skill, describe_result

        payload_dict = validated_payload.model_dump()
        result = execute_skill(skill_name, payload_dict)
        action_desc = describe_result(skill_name, result)
            
        # 7. Log Success
        StateTracker.log_execution_success(db, log_entry.id, result)
        
        state.skill_status = "SUCCESS"
        state.skill_result = result
        state.response = action_desc
        
    except Exception as e:
        error_msg = str(e)
        if "disabled by the administrator" in error_msg:
            state.skill_status = "DISABLED"
            state.response = (
                f"🚫 I understand you'd like me to execute **{skill_name}**. "
                f"However, this action is currently restricted by your care team's administrator.\n\n"
                f"**What you can do:**\n"
                f"- Contact your clinic directly at the front desk\n"
                f"- Ask your care coordinator to enable this feature"
            )
        else:
            state.skill_status = "FAILED"
            state.response = f"⚠️ I encountered an error while executing {skill_name}: {error_msg}"
            
        # Log failure if we got past auth and created a log entry
        try:
            if log_entry is not None:
                StateTracker.log_execution_failure(db, log_entry.id, error_msg)
        except Exception:
            pass
            
    finally:
        db.close()
        
    return state
