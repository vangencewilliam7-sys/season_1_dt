"""
core/schemas.py

THE CONTRACT between all layers.
This is the single source of truth for the PersonaManifest structure.

Rules:
- No domain-specific field names (no "patient", "candidate", "student")
- All fields are domain-agnostic
- This file must never import from adapters/ or runtime/
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime


class Heuristic(BaseModel):
    """
    One extracted decision-making pattern from the expert.
    The 'reasoning' field is the core value — it captures the WHY,
    not just the WHAT. This is the implicit knowledge that surveys miss.
    """
    trigger: str        # "When situation X occurs..."
    decision: str       # "...the expert typically does Y..."
    reasoning: str      # "...because of Z"  ← the implicit knowledge


class CommunicationStyle(BaseModel):
    """How the expert communicates — extracted from document tone analysis."""
    tone: List[str]             # e.g. ["direct", "analytical", "empathetic"]
    verbosity: str              # "concise" | "detailed" | "adaptive"
    preferred_framing: str      # e.g. "Always leads with risk before opportunity"


class Identity(BaseModel):
    """Who the expert is — populated by extraction, never hardcoded."""
    name: str
    role: str       # e.g. "Senior Recruiter", "Lead Cardiologist", "Principal Architect"
    domain: str     # e.g. "recruiting", "healthcare", "software_architecture"


class PersonaManifest(BaseModel):
    """
    The output artifact of the extraction framework.
    This is the ONLY thing this framework produces.
    Downstream systems (Digital Twin runtime, prompt assemblers) consume this.
    """
    # Identification
    expert_id: UUID = Field(default_factory=uuid4)
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(__import__("datetime").UTC))
    manifest_version: int = 1

    # Provenance — which documents were used for this extraction
    source_documents: List[str] = Field(
        default_factory=list,
        description="File paths, URLs, or record IDs of KB docs + Master Cases consumed"
    )

    # Core persona fields
    identity: Identity
    communication_style: CommunicationStyle
    heuristics: List[Heuristic] = Field(
        description="The expert's decision-making patterns — the heart of the Manifest"
    )

    # The drop zone — what this expert does NOT handle
    drop_zone_triggers: List[str] = Field(
        description="Topics or query types outside this expert's competence boundary"
    )

    # For downstream hat-switching (set per-expert during Shadow Mode calibration)
    confidence_threshold: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
        description="Minimum RAG confidence score to respond AS the expert vs. as Deputy"
    )

    # Shadow Mode quality gate
    shadow_approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


# ── Extraction Pipeline State ─────────────────────────────────────────────────

from typing import TypedDict, Any


class ExtractionState(TypedDict):
    """
    The shared state object passed between LangGraph nodes.
    Each node reads from this state and returns an updated copy.
    """
    expert_id: str
    domain: str
    documents: List[dict]               # Serialized Document objects from the reader
    behavioral_hypotheses: List[str]    # Output of IngestionNode
    generated_questions: List[dict]     # Output of JournalistNode
    expert_answers: List[dict]          # Input from Frontend (Expert manual answers)
    processed_findings: dict            # Output of AnswerProcessorNode
    final_manifest: Optional[dict]      # Output of CompilerNode (serialized Manifest)
    final_prompt: Optional[str]         # Output of Renderer
    error: Optional[str]                # Set if any node fails
    identity_override: dict             # Optional name/role sent in the request
