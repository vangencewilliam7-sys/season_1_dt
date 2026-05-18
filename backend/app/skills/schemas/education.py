"""
education.py — Education Domain Skill Payload Schemas
======================================================
All Pydantic models for Education-specific skills live here.
Dev C (Education) owns this file.

ADDING A NEW EDUCATION SKILL:
    1. Define the payload schema class below
    2. Register it in the EDUCATION_SKILL_REGISTRY dict at the bottom
    3. Create the functional skill in skills/functional/education/
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from uuid import UUID


# ── Base Skills (Education) ───────────────────────────────────────────────────
# TODO: Dev C — add Education-specific base skill payloads here.


# ── Functional Skills (Education) ─────────────────────────────────────────────
class SklStudentEngagementPayload(BaseModel):
    student_id: UUID
    persona: Literal["BEGINNER", "FAST_LEARNER", "EXAM_FOCUSED", "CAREER_SWITCH", "LOW_CONFIDENCE", "DEFAULT"] = Field(default="DEFAULT")
    interaction_type: Literal["QUERY_RESOLUTION", "PROACTIVE_ENGAGEMENT", "DEADLINE_NUDGE"]
    query_text: Optional[str] = Field(default=None, description="The student's incoming message, if any.")
    context_data: dict = Field(default_factory=dict, description="Additional context like course name, missed deadlines, or recent grades.")

class SklStudentMonitoringPayload(BaseModel):
    student_id: UUID
    persona: str = Field(default="DEFAULT")
    
    # Core Metrics
    login_frequency: int = Field(..., description="Logins in the last 7 days.")
    avg_score: float = Field(..., description="Current average assignment score.")
    missed_deadlines: int = Field(default=0)
    
    # Deep Intelligence Metrics (The WOW Factor)
    curiosity_coefficient: float = Field(default=0.5, description="0 to 1 score of question depth.")
    sentiment_trajectory: Literal["IMPROVING", "STABLE", "DECLINING"] = Field(default="STABLE")
    help_seeking_delay_days: int = Field(default=0, description="Days between friction and help request.")
    habit_consistency: float = Field(default=0.9, description="0 to 1 score of schedule stability.")

# ── Education Skill Registry ──────────────────────────────────────────────────
# Maps skill_name → payload schema for this domain.
# The central validation.py merges all domain registries automatically.

EDUCATION_SKILL_REGISTRY = {
    "SKL_STUDENT_ENGAGEMENT": SklStudentEngagementPayload,
    "SKL_STUDENT_MONITORING": SklStudentMonitoringPayload,
}
