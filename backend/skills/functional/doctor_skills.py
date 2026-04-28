"""
skills/functional/patient_followup_skill.py

FunctionalSkill — Doctor: Patient Follow-Up Communication
-----------------------------------------------------------
Expert: Fertility Doctor / Lead IVF Specialist
Base:   DraftSkill + NotifySkill

Sends a follow-up message to a patient, written in the doctor's tone,
grounded in the patient's retrieved case history from the Knowledge Hub.

Example trigger:
  "Send a follow-up to the patient about their Day 3 FSH results from yesterday's bloodwork."
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.interfaces.skill import FunctionalSkill, BaseSkill, SkillParams, SkillResult


class PatientFollowUpSkill(FunctionalSkill):
    """
    Functional skill: compose and send a patient follow-up in the doctor's voice.

    Wraps DraftSkill (to compose) + NotifySkill (to send).
    Persona context is injected at execution time — the draft will
    reflect the doctor's actual communication style.

    Input params:
        patient_name        : str   — Patient's first name
        patient_contact     : str   — Email or phone
        topic               : str   — "Day 3 bloodwork results", "Cycle day 10 scan"
        clinical_summary    : str   — Brief summary of the clinical data to communicate
        channel             : str   — "email" | "sms" | "in_app" (default: "email")
        urgency             : str   — "routine" | "time_sensitive" | "urgent"
    """

    def get_skill_id(self) -> str:
        return "doctor_patient_followup"

    def get_description(self) -> str:
        return (
            "Send a follow-up message to a patient about their clinical results, "
            "written in the doctor's tone and grounded in retrieved case history."
        )

    def get_scope_keywords(self) -> list[str]:
        # Block if the doctor's drop zone includes "billing" or "insurance"
        return ["billing", "insurance", "legal", "administrative"]

    def _enrich_params(self, params: SkillParams) -> SkillParams:
        """
        Inject doctor's communication style into the draft parameters.
        """
        persona = params.persona_context or {}
        comm_style = persona.get("communication_style", {})
        tone = ", ".join(comm_style.get("tone", ["professional", "empathetic"]))
        framing = comm_style.get("preferred_framing", "")
        phrases = comm_style.get("signature_phrases", [])

        p = params.raw_params
        enriched_params = {
            **p,
            "template": "patient_communication",
            "recipient": p.get("patient_contact", "patient@example.com"),
            "subject": f"Follow-up: {p.get('topic', 'Your Recent Visit')}",
            "tone_hint": tone,
            "key_points": [
                p.get("clinical_summary", ""),
                framing,
                f"Signature phrases to echo: {', '.join(phrases[:2])}",
                "Close with next steps and availability for questions.",
                "Remind patient this supplements — not replaces — their consultation.",
            ],
        }

        return SkillParams(
            raw_params=enriched_params,
            persona_context=params.persona_context,
            retrieved_cases=params.retrieved_cases,
        )

    def _post_process(self, result: SkillResult, params: SkillParams) -> SkillResult:
        """
        Tag the output with clinical source citations from retrieved cases.
        """
        if not result.success:
            return result

        sources = []
        if params.retrieved_cases:
            for case in params.retrieved_cases[:3]:
                if isinstance(case, dict):
                    sources.append({
                        "case_id": case.get("case_id", "unknown"),
                        "decision_summary": case.get("expert_decision", "")[:100],
                    })

        result.metadata["source_cases"] = sources
        result.metadata["persona_applied"] = True
        return result


class PatientPreCycleInstructionSkill(FunctionalSkill):
    """
    Functional skill: send pre-cycle preparation instructions to a patient.

    Example: "Send the standard pre-IVF cycle instructions to the patient
              who starts stimulation on Monday."

    ── PLACEHOLDER ──
    This skill is scaffolded. Functional body will be implemented
    once the base workflow is validated end-to-end.
    """

    def get_skill_id(self) -> str:
        return "doctor_pre_cycle_instructions"

    def get_description(self) -> str:
        return "Send standardized pre-cycle preparation instructions to a patient."

    def get_scope_keywords(self) -> list[str]:
        return ["billing", "insurance"]

    def _enrich_params(self, params: SkillParams) -> SkillParams:
        # ── PLACEHOLDER — to be implemented ──
        return params

    def _post_process(self, result: SkillResult, params: SkillParams) -> SkillResult:
        # ── PLACEHOLDER — to be implemented ──
        return result


class CaseEscalationSkill(FunctionalSkill):
    """
    Functional skill: escalate a query to the real doctor.

    Triggered automatically when confidence < threshold (fallback path).
    Notifies the doctor's coordinator with a structured brief.

    ── PLACEHOLDER ──
    """

    def get_skill_id(self) -> str:
        return "doctor_case_escalation"

    def get_description(self) -> str:
        return "Escalate a patient query or case to the real doctor's coordinator."

    def get_scope_keywords(self) -> list[str]:
        return []   # Escalation is always allowed — no drop zones block it

    def _enrich_params(self, params: SkillParams) -> SkillParams:
        # ── PLACEHOLDER — to be implemented ──
        return params

    def _post_process(self, result: SkillResult, params: SkillParams) -> SkillResult:
        # ── PLACEHOLDER — to be implemented ──
        return result


class TreatmentSummaryReportSkill(FunctionalSkill):
    """
    Functional skill: generate a structured treatment summary report for a patient.

    Example: "Generate a summary of this patient's IVF cycle — stimulation
              response, retrieval outcome, and transfer plan."

    ── PLACEHOLDER ──
    """

    def get_skill_id(self) -> str:
        return "doctor_treatment_summary"

    def get_description(self) -> str:
        return "Generate a structured treatment summary report in the doctor's voice."

    def get_scope_keywords(self) -> list[str]:
        return ["billing", "insurance", "legal"]

    def _enrich_params(self, params: SkillParams) -> SkillParams:
        # ── PLACEHOLDER — to be implemented ──
        return params

    def _post_process(self, result: SkillResult, params: SkillParams) -> SkillResult:
        # ── PLACEHOLDER — to be implemented ──
        return result


class KnowledgeGapFlagSkill(FunctionalSkill):
    """
    Functional skill: flag a knowledge gap back to the Knowledge Hub loop.

    When the Twin cannot answer with confidence AND no relevant Master Case
    exists, this skill creates a new Decision Gap entry — triggering the
    Divergence → Scenario → HITL loop for the doctor to resolve.

    ── PLACEHOLDER ──
    """

    def get_skill_id(self) -> str:
        return "doctor_flag_knowledge_gap"

    def get_description(self) -> str:
        return "Flag an unanswerable query as a knowledge gap for the doctor to resolve."

    def get_scope_keywords(self) -> list[str]:
        return []   # Gap flagging is always allowed

    def _enrich_params(self, params: SkillParams) -> SkillParams:
        # ── PLACEHOLDER — to be implemented ──
        return params

    def _post_process(self, result: SkillResult, params: SkillParams) -> SkillResult:
        # ── PLACEHOLDER — to be implemented ──
        return result
