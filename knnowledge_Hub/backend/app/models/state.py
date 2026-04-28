from pydantic import BaseModel, Field
from typing import List, Optional
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
    raw_chunks: List[DocumentChunk] = []
    decision_gaps: List[DecisionGap] = []
    synthetic_scenarios: List[SyntheticScenario] = []
    slm_audit_results: List[AuditResult] = []
    expert_transcripts: List[ExpertTranscript] = []
    parsed_cases: List[MasterCase] = []
    impact_classifications: List[ImpactArchetype] = []
    retry_count: int = 0
    audit_log: List[AuditEntry] = []
