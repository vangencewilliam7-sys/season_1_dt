"""
shared/schemas/knowledge.py

Shared data models for the Knowledge Hub pipeline output.
These schemas define the "output contracts" between KB stages.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
from enum import Enum


class ChunkLevel(int, Enum):
    """Heading hierarchy levels in the universal structure."""
    H1 = 1
    H2 = 2
    H3 = 3
    H4 = 4
    BODY = 99


class DocumentChunk(BaseModel):
    """
    Single unit from the Hierarchical Parser.
    Preserves full structural lineage — no context is ever lost.
    """
    chunk_id: UUID = Field(default_factory=uuid4)
    document_id: str
    expert_id: str

    content: str
    level: ChunkLevel
    heading_text: Optional[str] = None     # The actual heading label
    parent_id: Optional[UUID] = None       # None = top-level H1
    section_path: str = ""                 # "H1 Title > H2 Section > H3 Subsection"

    # Gap-preservation flag: True if this is a placeholder for a missing level
    is_structural_gap: bool = False

    source_path: str = ""                  # Original file path or URL
    page_number: Optional[int] = None
    char_offset: Optional[int] = None

    # Embedding (populated by EmbeddingService)
    embedding: Optional[List[float]] = None
    embedding_model: Optional[str] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MasterCase(BaseModel):
    """
    An expert's crystallized decision — the output of the HITL loop.
    This is what the RAG pipeline retrieves at query time.
    """
    case_id: UUID = Field(default_factory=uuid4)
    expert_id: str
    scenario_id: str                       # The scenario that prompted this response
    source_chunk_id: str                   # The KB chunk that triggered the scenario

    # The expert's structured decision
    expert_decision: str
    chain_of_thought: List[str] = Field(
        default_factory=list,
        description="Step-by-step reasoning path extracted from transcript"
    )
    logic_tags: List[str] = Field(
        default_factory=list,
        description="Categorical tags: ['risk-first', 'data-driven', 'protocol-adherent']"
    )
    confidence_note: Optional[str] = None  # Expert's own stated confidence level

    # Impact classification (set during Visual Audit gate)
    impact_type: Optional[str] = None      # "safety" | "structural" | "informational"

    # Embedding for RAG retrieval
    embedding: Optional[List[float]] = None

    # Versioning
    version: int = 1
    superseded_by: Optional[UUID] = None   # If this case was later corrected
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionGap(BaseModel):
    """
    A soft-rule marker found by the Divergence Scanner.
    Represents implicit expert knowledge waiting to be surfaced.
    """
    gap_id: UUID = Field(default_factory=uuid4)
    source_chunk_id: str
    gap_type: str                          # "ambiguous_rule", "soft_protocol", "conditional"
    ambiguous_text: str                    # The exact text containing "usually", "typically"
    generated_scenario: Optional[str] = None  # Scenario generated to resolve this gap
    resolved: bool = False
