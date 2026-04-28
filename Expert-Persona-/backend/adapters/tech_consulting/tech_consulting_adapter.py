"""
adapters/tech_consulting/tech_consulting_adapter.py

Tech Consulting & Architecture Domain Adapter.

Focuses on:
- System design and architectural patterns
- Non-functional requirements (scalability, security, maintainability)
- Technology selection and trade-off analysis
- Strategic technical leadership
"""

from adapters.base_adapter import DomainAdapter


class TechConsultingAdapter(DomainAdapter):
    """
    Adapter for Tech Consulting and Software Architecture vertical.
    """

    def get_domain_id(self) -> str:
        return "tech_consulting"

    def get_immutable_rules(self) -> str:
        return """
SYSTEM RULES (NON-OVERRIDABLE):
- Architecture Principles: Prioritize 'Simplicity' and 'Maintainability' unless high-scale requirements are explicitly proven.
- Vendor Neutrality: Avoid hardcoding vendor-specific solutions (e.g., AWS, GCP, Azure) unless the context requires it. Always state the architectural pattern first (e.g., 'Managed Pub/Sub').
- Security First: Any architectural recommendation must include a mention of its impact on the attack surface or data security.
- Scope: Focus on high-level architecture and strategy. Do not provide line-by-line code optimization or bug fixes.
        """.strip()

    def get_fallback_identity(self) -> dict:
        return {
            "role": "Consulting Associate / Junior Engineer",
            "tone": "helpful, detail-oriented, analytical",
            "action": "State that the architectural trade-off requires a Principal Architect's deeper review. Offer to document the current constraints and research the top 3 industry patterns for the expert to evaluate."
        }

    def get_extraction_context(self) -> str:
        return """
This expert is a Principal Architect, CTO, or Senior Technical Consultant with 20+ years of experience.

During extraction, probe for:
- Design Heuristics: How do they choose between microservices and monoliths? What specific 'smells' trigger a refactor?
- Technology Selection: What is their process for evaluating a new framework or database?
- Scalability Patterns: How do they approach bottlenecks (database, network, execution)?
- Legacy Modernization: How do they decide when to 'strangle' a legacy app vs. 'rip and replace'?
- Stakeholder Management: How do they communicate technical risk to non-technical business leaders?

Scenario questions should involve complex, high-stakes system failures or zero-day migrations where there are no 'correct' answers, only trade-offs.
        """.strip()
