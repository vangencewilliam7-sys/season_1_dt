from typing import Dict, Any, List
import json
import os

class ContextManager:
    """
    Manages industry-specific 'Context Packs' to keep the core engine agnostic.
    """
    def __init__(self, industry: str = "universal"):
        self.industry = industry
        self.contexts = {
            "universal": {
                "domain_name": "Professional Services Hub",
                "expert_role": "Senior Principal Specialist",
                "semantic_markers": [
                    r"\btypically\b", r"\bgenerally\b", r"\busually\b", 
                    r"\boptimal\b", r"\bconsider\b", r"\bstandard practice\b"
                ],
                "risk_keywords": ["critical", "failure", "blocker", "compliance"],
                "decision_archetypes": ["Strategic", "Operational", "Tactical"]
            },
            "fertility": {
                "domain_name": "Fertility Clinical Triage",
                "expert_role": "Senior Reproductive Endocrinologist",
                "semantic_markers": [
                    r"\btypically\b", r"\bgenerally\b", r"\busually\b", 
                    r"\bmost cases\b", r"\bconsider\b", r"\boften\b"
                ],
                "risk_keywords": ["bleeding", "pain", "fever", "emergency"],
                "decision_archetypes": ["Safety", "Structural", "Informational"]
            },
            "legal": {
                "domain_name": "Corporate Law Compliance",
                "expert_role": "Senior Corporate Counsel",
                "semantic_markers": [
                    r"\bsubject to\b", r"\bat the discretion of\b", r"\bunreasonable\b", 
                    r"\bmaterial\b", r"\btypically\b"
                ],
                "risk_keywords": ["breach", "liability", "lawsuit", "sanction"],
                "decision_archetypes": ["Statutory", "Discretionary", "Procedural"]
            }
        }

    def get_context(self) -> Dict[str, Any]:
        """Returns the context dictionary for the current industry."""
        return self.contexts.get(self.industry, self.contexts["universal"])

    def get_prompt_jacket(self, base_instruction: str) -> str:
        """Surrounds a base instruction with industry-specific context."""
        ctx = self.get_context()
        return f"""
        Domain: {ctx['domain_name']}
        Expert Role: {ctx['expert_role']}
        
        Instruction: {base_instruction}
        """
