"""
healthcare.py — Healthcare Domain Skill Payload Schemas
========================================================
All Pydantic models for Healthcare-specific skills live here.
Dev A (Healthcare) owns this file.

ADDING A NEW HEALTHCARE SKILL:
    1. Define the payload schema class below
    2. Register it in the HEALTHCARE_SKILL_REGISTRY dict at the bottom
    3. Create the functional skill in skills/functional/healthcare/
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from uuid import UUID


# ── Base Skills (Healthcare) ──────────────────────────────────────────────────

class BookAppointmentPayload(BaseModel):
    patient_id: UUID
    appointment_time: datetime = Field(description="ISO-8601 string, must be in the future")
    reason_code: Literal["CONSULT", "FOLLOW_UP", "URGENT"]


class ActVisionOcrPayload(BaseModel):
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    extraction_type: Literal["VITALS", "LAB_RESULTS", "GENERAL_TEXT"]


class KnwReportSynthesisPayload(BaseModel):
    patient_id: UUID
    data_sources: List[str] = Field(description="List of IDs or references to the data sources")


class ActChecklistVerifyPayload(BaseModel):
    patient_id: UUID
    required_documents: List[str] = Field(description="List of document types that must be present")


# ── Functional Skills (Healthcare) ────────────────────────────────────────────

class SklPreOpGatekeeperPayload(BaseModel):
    patient_id: UUID
    surgery_date: datetime = Field(description="ISO-8601 string, date of scheduled surgery")
    required_documents: List[str] = Field(description="Checklist of required pre-op documents")


class SklExpertSynthesisPayload(BaseModel):
    patient_id: UUID
    data_sources: List[str] = Field(description="List of IDs or references to the data sources")
    release_approved: bool = Field(description="Safety toggle. Must be True to dispatch externally.")


class SklBaselineVigilancePayload(BaseModel):
    patient_id: UUID
    baseline_thresholds: dict = Field(
        description="Patient-specific baseline ranges, e.g. {'bp_systolic': [100, 140], 'hr': [60, 100]}"
    )
    image_url: Optional[str] = Field(default=None, description="URL of bedside monitor image for OCR")


# ── Healthcare Skill Registry ─────────────────────────────────────────────────
# Maps skill_name → payload schema for this domain.
# The central validation.py merges all domain registries automatically.

HEALTHCARE_SKILL_REGISTRY = {
    "book_appointment":         BookAppointmentPayload,
    "ACT_VISION_OCR":           ActVisionOcrPayload,
    "KNW_REPORT_SYNTHESIS":     KnwReportSynthesisPayload,
    "ACT_CHECKLIST_VERIFY":     ActChecklistVerifyPayload,
    "SKL_PRE_OP_GATEKEEPER":    SklPreOpGatekeeperPayload,
    "SKL_EXPERT_SYNTHESIS":     SklExpertSynthesisPayload,
    "SKL_BASELINE_VIGILANCE":   SklBaselineVigilancePayload,
}
