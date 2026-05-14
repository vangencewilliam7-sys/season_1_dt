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
# TODO: Dev C — add Education-specific functional skill payloads here.
# Examples:
#
# class SklMasteryCheckPayload(BaseModel):
#     student_id: UUID
#     topic_id: str
#     session_id: UUID
#     difficulty_level: Literal["BEGINNER", "INTERMEDIATE", "ADVANCED"]
#
# class SklLearningGapDetectorPayload(BaseModel):
#     student_id: UUID
#     assessment_results: List[dict] = Field(description="Array of {topic, score, max_score}")
#     detect_prerequisites: bool = Field(default=True)


# ── Education Skill Registry ──────────────────────────────────────────────────
# Maps skill_name → payload schema for this domain.
# The central validation.py merges all domain registries automatically.

EDUCATION_SKILL_REGISTRY = {
    # "SKL_MASTERY_CHECK":         SklMasteryCheckPayload,
    # "SKL_LEARNING_GAP_DETECTOR": SklLearningGapDetectorPayload,
}
