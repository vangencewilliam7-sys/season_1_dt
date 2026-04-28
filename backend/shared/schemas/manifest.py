"""
shared/schemas/manifest.py

THE CONTRACT between all layers.
---------------------------------
PersonaManifest is the single output artifact of the Expert Persona framework.
Every downstream consumer (retrieval, skills, chat) reads from this schema.

Rules:
  - No domain-specific field names (no "patient", "candidate", "student")
  - All fields must be domain-agnostic
  - This schema is LOCKED — changes require incrementing manifest_version
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone


class Heuristic(BaseModel):
    """
    One extracted decision-making pattern.
    The 'reasoning' field is where implicit knowledge lives —
    it captures the WHY that surveys and documents never capture.
    """
    trigger: str        # "When situation X occurs..."
    decision: str       # "...the expert typically does Y..."
    reasoning: str      # "...because of Z"   ← the implicit knowledge


class CommunicationStyle(BaseModel):
    """
    How this expert communicates.
    Extracted from document tone + conversational interview.
    """
    tone: List[str]             # ["direct", "empathetic", "evidence-based"]
    verbosity: str              # "concise" | "detailed" | "adaptive"
    preferred_framing: str      # "Always leads with risk before opportunity"
    signature_phrases: List[str] = Field(
        default_factory=list,
        description="Recurring phrases or analogies unique to this expert"
    )


class Identity(BaseModel):
    """Who the expert is — always extracted, never hardcoded."""
    name: str
    role: str       # "Lead Fertility Specialist", "Senior Recruiter"
    domain: str     # "healthcare", "recruiting", "tech_consulting"
    specialization: Optional[str] = None  # Sub-domain: "IVF", "Tech Hiring"


class PersonaManifest(BaseModel):
    """
    The output artifact of the Persona Extraction framework.

    Downstream systems consume this. It is:
      - Stored in Supabase (persona_manifests table)
      - Loaded at query time for 3-Layer Prompt Assembly
      - Versioned and expert-approved via Shadow Mode
    """

    # ── Identity ─────────────────────────────────────────────────────────────
    expert_id: UUID = Field(default_factory=uuid4)
    extracted_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    manifest_version: int = 1
    source_documents: List[str] = Field(
        default_factory=list,
        description="IDs/paths of KB chunks + Master Cases used in this extraction"
    )

    # ── Persona Core ─────────────────────────────────────────────────────────
    identity: Identity
    communication_style: CommunicationStyle
    heuristics: List[Heuristic] = Field(
        description="The expert's decision-making patterns — the heart of the Manifest"
    )
    drop_zone_triggers: List[str] = Field(
        description="Topics/query types outside this expert's competence boundary"
    )

    # ── Runtime Config ───────────────────────────────────────────────────────
    confidence_threshold: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
        description="Minimum RAG confidence to respond AS the expert vs. as Deputy"
    )

    # ── Quality Gate ─────────────────────────────────────────────────────────
    shadow_approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
