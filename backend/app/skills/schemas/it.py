"""
it.py — IT Domain Skill Payload Schemas
=========================================
All Pydantic models for IT-specific skills live here.
Dev B (IT) owns this file.

ADDING A NEW IT SKILL:
    1. Define the payload schema class below
    2. Register it in the IT_SKILL_REGISTRY dict at the bottom
    3. Create the functional skill in skills/functional/it/
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from uuid import UUID


# ── Base Skills (IT) ──────────────────────────────────────────────────────────

class SendCommunicationPayload(BaseModel):
    """Generic communication dispatch — shared across domains but owned by IT for now."""
    template_id: str
    recipient_address: str = Field(description="Email or WhatsApp number")
    dynamic_vars: dict = Field(default_factory=dict, description="Variables for the template")


# ── Functional Skills (IT) ────────────────────────────────────────────────────
class SklItProjectPredictionPayload(BaseModel):
    project_id: UUID
    
    # Execution Metrics
    velocity_delta: float = Field(..., description="Change in team velocity vs previous sprint (%)")
    requirement_churn: float = Field(..., description="Percentage of requirements changed mid-sprint")
    dependency_lag_days: int = Field(default=0, description="Total days stalled due to external dependencies")
    
    # Deep Metrics
    qa_failure_rate: float = Field(default=0.05, description="Percentage of tickets failing QA on first pass")
    documentation_completeness: float = Field(default=0.8, description="0 to 1 score of technical documentation readiness")
    team_burnout_risk: float = Field(default=0.1, description="0 to 1 score based on overtime and sentiment")

# ── IT Skill Registry ─────────────────────────────────────────────────────────
# Maps skill_name → payload schema for this domain.
# The central validation.py merges all domain registries automatically.

IT_SKILL_REGISTRY = {
    "send_communication": SendCommunicationPayload,
    "SKL_IT_PROJECT_PREDICTION": SklItProjectPredictionPayload,
}
