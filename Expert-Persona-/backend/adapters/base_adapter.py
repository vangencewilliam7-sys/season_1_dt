"""
adapters/base_adapter.py

THE PLUGIN CONTRACT for Layer 2.

To add a new vertical to the framework:
  1. Create adapters/<your_domain>/<your_domain>_adapter.py
  2. Subclass DomainAdapter
  3. Implement all 4 abstract methods
  4. Run: pytest tests/test_adapter_contract.py --adapter=<your_domain>
  5. All tests pass = framework-compliant

That is the ENTIRE integration cost for a new domain.
"""

from abc import ABC, abstractmethod


class DomainAdapter(ABC):
    """
    Abstract plugin contract for Layer 2.

    The framework calls ONLY these 4 methods.
    No other knowledge of the domain is needed or allowed in Layer 1.
    """

    @abstractmethod
    def get_domain_id(self) -> str:
        """
        Unique slug identifying this domain.
        Examples: 'healthcare', 'recruiting', 'course_platform', 'legal'
        Used for logging, routing, and manifest tagging.
        """

    @abstractmethod
    def get_immutable_rules(self) -> str:
        """
        Non-overridable constraints for this domain.

        These are prepended to EVERY LLM prompt in the extraction pipeline.
        The Persona Manifest CANNOT soften, override, or contradict these rules.

        Include here:
        - Compliance constraints (e.g. HIPAA, GDPR, EEOC)
        - Ethical boundaries
        - Scope limits specific to this domain
        - Liability guardrails

        Returns a plain string (not JSON).
        """

    @abstractmethod
    def get_fallback_identity(self) -> dict:
        """
        The Deputy persona — who the Digital Twin becomes when a query
        falls outside the expert's competence (confidence < threshold).

        This is used by downstream runtime systems (hat-switching router).
        The extraction framework records this in the Manifest for downstream use.

        Returns a dict with keys:
            role (str): The fallback role name
            tone (str): How the fallback communicates
            action (str): What the fallback does (defer, escalate, redirect)

        Example:
            {"role": "Recruiting Coordinator",
             "tone": "neutral, process-oriented",
             "action": "Acknowledge the gap and route to the senior recruiter"}
        """

    @abstractmethod
    def get_extraction_context(self) -> str:
        """
        Domain-specific framing injected into the AI Journalist's prompt.

        This tells the Journalist WHAT KIND of scenarios to probe.
        Without this, the journalist asks generic questions.
        With this, it asks questions specific to the expert's actual domain.

        Example for recruiting:
            "This expert is a technical recruiter. Probe scenarios around:
             candidate evaluation, sourcing strategy, offer negotiation,
             pipeline management, and hiring manager relationships."

        Returns a plain string (not JSON).
        """
