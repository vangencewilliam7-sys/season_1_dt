from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from .schemas import (
    DocumentChunk, 
    DecisionGap, 
    SyntheticScenario, 
    AuditResult, 
    ExpertTranscript, 
    MasterCase, 
    AuditEntry
)
from .enums import ImpactArchetype

class GraphState(BaseModel):
    document_id: str
    category: str = "base_knowledge"
    source_path: Optional[str] = None   # Absolute path to the uploaded file — set by ingest API

    # ── Domain Identity (injected at API boundary via DomainAdapter) ──────────
    # These are plain strings/dicts so GraphState stays fully JSON-serialisable.
    # The Universal Core nodes must NEVER import from adapters/.
    domain_id: Optional[str] = None        # FK → domains.id (e.g. healthcare UUID)
    role_id: Optional[str] = None          # FK → roles.id   (e.g. doctor UUID)
    adapter_context: Optional[Dict[str, Any]] = None  # Serialised adapter metadata

    # ── Pipeline Data ─────────────────────────────────────────────────────────
    raw_chunks: List[DocumentChunk] = []
    decision_gaps: List[DecisionGap] = []
    synthetic_scenarios: List[SyntheticScenario] = []
    slm_audit_results: List[AuditResult] = []
    expert_transcripts: List[ExpertTranscript] = []
    parsed_cases: List[MasterCase] = []
    impact_classifications: List[ImpactArchetype] = []
    retry_count: int = 0
    audit_log: List[AuditEntry] = []
