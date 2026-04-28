"""
adapters/recruiting/recruiting_adapter.py

Recruiting (HR) Domain Adapter.

Focuses on:
- Candidate evaluation & sourcing heuristics
- Unbiased screening (EEOC compliance)
- Talent acquisition process rules
- ATS (Applicant Tracking System) logic
"""

from adapters.base_adapter import DomainAdapter


class RecruitingAdapter(DomainAdapter):
    """
    Adapter for the Recruiting/HR vertical.
    """

    def get_domain_id(self) -> str:
        return "recruiting"

    def get_immutable_rules(self) -> str:
        return """
SYSTEM RULES (NON-OVERRIDABLE):
- Compliance: Strictly adhere to EEOC guidelines. Never reference protected characteristics (age, gender, ethnicity, religion).
- Decision Limit: Do not make final hiring decisions. Provide signals, scores, and evidence-based summaries only.
- Privacy: Mask PII (Personal Identifiable Information) where candidate consent is not explicitly verified.
- Neutrality: Maintain a professional, objective tone at all times.
        """.strip()

    def get_fallback_identity(self) -> dict:
        return {
            "role": "Recruiting Coordinator",
            "tone": "neutral, process-oriented, empathetic",
            "action": "Acknowledge the specific query gap, state that it requires a Senior Recruiter's review, and offer to log it in the ATS for follow-up."
        }

    def get_extraction_context(self) -> str:
        return """
This expert is a Senior Recruiter or Talent Acquisition Partner. 

During extraction, probe for:
- Sourcing heuristics: How do they find 'diamond in the rough' candidates?
- Evaluation patterns: What specific technical or cultural signals are they looking for in a CV or interview transcript?
- Negotiation style: How do they handle salary expectations and closing?
- Candidate Experience: How do they handle rejection or high-touch engagement?
- Bias mitigation: How do they ensure an objective evaluation?

Scenario questions should focus on difficult trade-offs (e.g., strong skills vs poor culture fit) and specific sourcing challenges.
        """.strip()
