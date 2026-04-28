from typing import List, Optional
from pydantic import BaseModel, Field

class ChatState(BaseModel):
    expert_id: str
    session_id: str
    query: str
    
    # Internal Trajectory
    retrieved_cases: List[dict] = Field(default_factory=list)
    rationale: str = ""
    
    # Final Output
    response: str = ""
    confidence: float = 0.0
    persona_mode: str = "offline"
