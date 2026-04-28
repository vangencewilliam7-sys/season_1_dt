"""
adapters/_reference_impl/generic_adapter.py

REFERENCE IMPLEMENTATION — Generic Adapter

A blank-slate, domain-agnostic adapter for:
1. Testing Layer 1 (extraction nodes) in complete isolation
2. Serving as a copy-paste starting point for new domain adapters
3. Running end-to-end tests without a real domain context

This adapter makes NO assumptions about the expert's domain.
Use it only for testing and development — not for production deployments.
"""

from adapters.base_adapter import DomainAdapter


class GenericAdapter(DomainAdapter):
    """
    Blank-slate adapter — no domain knowledge.
    Useful for testing the extraction engine without a real domain.
    """

    def get_domain_id(self) -> str:
        return "generic"

    def get_immutable_rules(self) -> str:
        return """
SYSTEM RULES (NON-OVERRIDABLE):
- This is a generic extraction context. No domain-specific rules apply.
- Do not fabricate information not present in the source documents.
- Always flag uncertainty explicitly rather than guessing.
- Respect the expert's stated knowledge boundaries.
        """.strip()

    def get_fallback_identity(self) -> dict:
        return {
            "role": "General Support Agent",
            "tone": "neutral, helpful",
            "action": "Acknowledge the question is outside scope and suggest the user consult a specialist"
        }

    def get_extraction_context(self) -> str:
        return """
This is a generic expert extraction. The expert's domain is not yet specified.

During extraction, probe for:
- General decision-making patterns and heuristics
- Communication and reasoning style
- Knowledge boundaries and areas of deference
- Risk tolerance and thresholds
- How the expert handles uncertainty

Ask broad, scenario-based questions that reveal reasoning process
rather than domain-specific knowledge.
        """.strip()
