from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ChatState(BaseModel):
    expert_id:  str
    session_id: str
    query:      str

    # ── Domain Identity (injected at chat API boundary) ───────────────────────
    domain_id:       Optional[str]            = None
    role_id:         Optional[str]            = None
    workflow_id:     Optional[str]            = None
    task_id:         Optional[str]            = None
    adapter_context: Optional[Dict[str, Any]] = None  # Includes system_prompt, fallback, threshold

    # ── Validation & Triage Levels ────────────────────────────────────────────
    is_valid:        bool                     = True
    triage_level:    str                      = "GREEN_ZONE" # GREEN_ZONE | YELLOW_ZONE | RED_ZONE

    # ── Internal Trajectory ───────────────────────────────────────────────────
    retrieved_cases: List[dict] = Field(default_factory=list)
    rationale: str = ""
    
    # NEW: Intent Detection
    intent_type: str = "knowledge"  # "knowledge" | "action"
    detected_skill: str = ""        # e.g. "book_appointment"
    extracted_params: Dict[str, Any] = Field(default_factory=dict)
    
    # NEW: Skill Execution Results
    skill_result: Optional[Dict[str, Any]] = None
    skill_status: str = ""          # "SUCCESS" | "FAILED" | "DISABLED"
    
    # ── Final Output ──────────────────────────────────────────────────────────
    response:     str   = ""
    confidence:   float = 0.0
    persona_mode: str   = "offline"

    # ── Proxy Evidence Gathering (Low Data State) ─────────────────────────────
    low_data_mode:        bool           = False
    missing_metrics:      List[str]      = Field(default_factory=list)
    accumulated_evidence: Dict[str, Any] = Field(default_factory=dict)
    likelihood_score:     str            = ""

