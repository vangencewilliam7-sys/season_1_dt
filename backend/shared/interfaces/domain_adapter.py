"""
shared/interfaces/domain_adapter.py

SOLID — Open/Closed Principle
------------------------------
The framework is OPEN for extension (new domain = new adapter file)
but CLOSED for modification (adding healthcare never touches core code).

Every new vertical implements exactly 4 methods. That is the complete
integration cost for any new domain.
"""

from abc import ABC, abstractmethod


class DomainAdapter(ABC):
    """
    Plugin contract for domain-specific behavior.

    Implement this to add any new expert vertical.
    The framework ONLY calls these 4 methods — nothing else.

    Current implementations:
      - HealthcareAdapter     (Doctor / Fertility / HIPAA)
      - RecruitingAdapter     (Senior Recruiter / ATS)
      - TechConsultingAdapter (Principal Architect)
      - GenericAdapter        (Blank-slate — for testing)
    """

    @abstractmethod
    def get_domain_id(self) -> str:
        """
        Unique slug for this domain.
        Used as a key in config and routing.
        Example: 'healthcare', 'recruiting', 'course_platform'
        """

    @abstractmethod
    def get_immutable_rules(self) -> str:
        """
        Non-overridable constraints prepended to EVERY prompt.
        These cannot be softened by persona data or user input.

        Healthcare example:
            "Never recommend a specific dosage. Always defer complex
             medical decisions to the supervising physician."

        These are the system's legal and ethical guardrails.
        """

    @abstractmethod
    def get_fallback_identity(self) -> dict:
        """
        Who the Twin becomes when a query is out of scope (confidence < threshold).

        Schema:
            {
                "role":   str,   # "Duty Nurse", "HR Coordinator", "Support Engineer"
                "tone":   str,   # "empathetic, deferential", "professional, direct"
                "action": str    # What the fallback persona does: "Flag for Lead Doctor"
            }
        """

    @abstractmethod
    def get_extraction_context(self) -> str:
        """
        Domain framing injected into the AI Journalist's system prompt.
        Tells the Journalist what kinds of scenarios to generate for this domain.

        Healthcare example:
            "Focus on clinical decision-making scenarios: patient edge cases,
             protocol ambiguities, multi-symptom presentations, referral decisions."
        """
