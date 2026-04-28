from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from .enums import ImpactArchetype, RiskLevel, AuditStatus

class DocumentChunk(BaseModel):
    id: str
    content: str
    parent_id: Optional[str] = None
    level: int = 0
    source_path: str
    metadata: Dict[str, Any] = {}

class DecisionGap(BaseModel):
    id: str
    gap_type: str
    ambiguous_text: str
    source_chunk_id: str

class SyntheticScenario(BaseModel):
    id: str
    gap_id: str
    scenario_text: str
    variables: Dict[str, Any] = {}

class AuditResult(BaseModel):
    scenario_id: str
    status: AuditStatus
    feedback: str

class ExpertTranscript(BaseModel):
    scenario_id: str
    raw_text: str
    audio_url: Optional[str] = None

class MasterCase(BaseModel):
    expert_decision: str
    chain_of_thought: List[str]
    logic_tags: List[str]
    confidence_note: Optional[str] = None
    source_chunk_id: str
    scenario_id: str

class AuditEntry(BaseModel):
    node: str
    timestamp: str
    action: str
    details: str
