"""
presales.py — Pre-Sales Domain Skill Payload Schemas
======================================================
All Pydantic models for Pre-Sales-specific skills live here.
Dev D (Pre-Sales) owns this file.

ADDING A NEW PRE-SALES SKILL:
    1. Define the payload schema class below
    2. Register it in the PRESALES_SKILL_REGISTRY dict at the bottom
    3. Create the functional skill in skills/functional/presales/
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from uuid import UUID


# ── Functional Skills (Pre-Sales) ─────────────────────────────────────────────
# TODO: Dev D — add Pre-Sales-specific skill payloads here.
# Examples:
#
# class SklTechStackInferencePayload(BaseModel):
#     prospect_id: UUID
#     website_url: str = Field(description="Client website URL for tech stack inference")
#     linkedin_url: Optional[str] = None
#
# class SklDiscoveryBriefPayload(BaseModel):
#     prospect_id: UUID
#     requirements: List[str] = Field(description="Client requirements extracted from RFP")
#     budget_range: Optional[str] = None
#
# class SklReferenceMatchPayload(BaseModel):
#     prospect_id: UUID
#     tech_stack: List[str] = Field(description="Inferred or stated client tech stack")
#     domain_vertical: Literal["FINTECH", "HEALTHCARE", "ECOMMERCE", "SAAS", "OTHER"]


# ── Pre-Sales Skill Registry ──────────────────────────────────────────────────
# Maps skill_name → payload schema for this domain.
# The central validation.py merges all domain registries automatically.

PRESALES_SKILL_REGISTRY = {
    # "SKL_TECH_STACK_INFERENCE": SklTechStackInferencePayload,
    # "SKL_DISCOVERY_BRIEF":     SklDiscoveryBriefPayload,
    # "SKL_REFERENCE_MATCH":     SklReferenceMatchPayload,
}
