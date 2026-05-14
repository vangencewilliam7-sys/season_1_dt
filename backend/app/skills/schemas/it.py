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
# TODO: Dev B — add IT-specific functional skill payloads here.
# Examples:
#
# class SklSprintRiskMonitorPayload(BaseModel):
#     project_id: UUID
#     sprint_number: int
#     risk_threshold: float = Field(default=0.7, description="Minimum risk score to trigger alert")
#
# class SklEscalationBriefPayload(BaseModel):
#     project_id: UUID
#     blocker_description: str
#     severity: Literal["HIGH", "CRITICAL"]


# ── IT Skill Registry ─────────────────────────────────────────────────────────
# Maps skill_name → payload schema for this domain.
# The central validation.py merges all domain registries automatically.

IT_SKILL_REGISTRY = {
    "send_communication": SendCommunicationPayload,
    # "SKL_SPRINT_RISK_MONITOR": SklSprintRiskMonitorPayload,
    # "SKL_ESCALATION_BRIEF":    SklEscalationBriefPayload,
}
