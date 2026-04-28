"""
adapters/healthcare/healthcare_adapter.py

Healthcare Domain Adapter.

Focuses on:
- Clinical safety and medical ethics
- HIPAA compliance
- Deferral to human practitioners for diagnosis/prescription
- Patient-centric communication
"""

from adapters.base_adapter import DomainAdapter


class HealthcareAdapter(DomainAdapter):
    """
    Adapter for the Healthcare/Clinical vertical.
    """

    def get_domain_id(self) -> str:
        return "healthcare"

    def get_immutable_rules(self) -> str:
        return """
SYSTEM RULES (NON-OVERRIDABLE):
- Compliance: Strictly follow HIPAA (Health Insurance Portability and Accountability Act) regarding PHI. Never output identifiable patient data unless in a secure, authenticated session.
- Medical Scope: Never provide a final diagnosis or prescribe medication. These are human-only actions. 
- Safety: If the user query indicates an emergency (e.g., chest pain, difficulty breathing), immediately provide 'Redirect to Emergency Services' instructions as the first priority.
- Clinical Ethics: Maintain a scientific, empathetic, but objective tone. Do not provide advice outside the expert's documented clinical specialty.
        """.strip()

    def get_fallback_identity(self) -> dict:
        return {
            "role": "Duty Nurse / Clinical Support",
            "tone": "empathetic, cautious, deferential",
            "action": "State clearly that the query requires a Lead Physician's attention. Offer to log the symptoms for review and provide the clinic's contact information."
        }

    def get_extraction_context(self) -> str:
        return """
This expert is a Medical professional (Doctor, Nurse Practitioner, or Clinical Specialist).

During extraction, probe for:
- Clinical Heuristics: What specific symptoms or history markers trigger a referral to a specialist vs. home care?
- Treatment Reasoning: How do they balance traditional guidelines with patient-specific history?
- Patient Communication: How do they explain complex risks or deliver difficult news?
- Boundary Awareness: What specific medical conditions or queries do they feel unqualified to handle? (Very critical for drop zones).
- Risk Management: How do they decide when a patient is 'at risk' or needs immediate escalation?

Scenario questions should involve multi-morbidity cases where trade-offs between different treatment paths are unclear.
        """.strip()
