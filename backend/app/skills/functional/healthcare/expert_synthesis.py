"""
expert_synthesis.py — SKL_EXPERT_SYNTHESIS Functional Skill
============================================================
3-step workflow: aggregate data → format expert brief → conditional dispatch.
Composes: KNW_REPORT_SYNTHESIS + send_communication

Owner: Dev A (Healthcare)
"""
from typing import Dict, Any
from app.skills.functional.base_skill import BaseFunctionalSkill
from app.skills.wrappers.clinical_services import ClinicalServicesWrapper
from app.skills.wrappers.email_service import EmailServiceWrapper


class ExpertSynthesis(BaseFunctionalSkill):

    @staticmethod
    def skill_name() -> str:
        return "SKL_EXPERT_SYNTHESIS"

    @staticmethod
    def _format_expert_brief(raw_data: Dict[str, Any], patient_id: str) -> Dict[str, Any]:
        """
        Deterministic Expert Lens Formatter.
        Transforms raw aggregated clinical data into a structured
        clinical brief using the expert's preferred format.
        This is pure formatting — no LLM reasoning involved.
        """
        lab = raw_data.get("lab_results", "N/A")
        vitals = raw_data.get("vitals_summary", "N/A")
        notes = raw_data.get("last_visit_notes", "N/A")

        brief_text = (
            f"=== EXPERT CLINICAL BRIEF ===\n"
            f"Patient ID : {patient_id}\n"
            f"----------------------------\n"
            f"LAB RESULTS  : {lab}\n"
            f"VITALS       : {vitals}\n"
            f"CLINICAL NOTE: {notes}\n"
            f"============================\n"
        )

        return {
            "brief_text": brief_text,
            "sections": {
                "lab_results": lab,
                "vitals_summary": vitals,
                "clinical_notes": notes,
            },
        }

    @staticmethod
    def execute(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrates SKL_EXPERT_SYNTHESIS
        Step 1: Aggregate clinical data via KNW_REPORT_SYNTHESIS
        Step 2: Format as Expert Clinical Brief (Expert Lens)
        Step 3: Dispatch externally — ONLY if release_approved is True
        """
        print("\n--- [ORCHESTRATOR] Starting SKL_EXPERT_SYNTHESIS ---")

        patient_id = str(payload["patient_id"])
        data_sources = payload["data_sources"]
        release_approved = payload.get("release_approved", False)

        # ── Step 1: Data Aggregation ──────────────────────────────
        try:
            synthesis_result = ClinicalServicesWrapper.synthesize_report({
                "patient_id": patient_id,
                "data_sources": data_sources,
            })
            raw_data = synthesis_result.get("raw_data", {})
            print("[ORCHESTRATOR] Step 1 — Report synthesis complete.")
        except Exception as e:
            print(f"[ORCHESTRATOR] Step 1 FAILED — Report synthesis: {str(e)}")
            raise Exception(
                f"Expert Synthesis Halted at Step 1 (Data Aggregation): {str(e)}"
            )

        # ── Step 2: Expert Lens Formatting ────────────────────────
        try:
            expert_brief = ExpertSynthesis._format_expert_brief(
                raw_data, patient_id
            )
            print("[ORCHESTRATOR] Step 2 — Expert brief formatted.")
        except Exception as e:
            print(f"[ORCHESTRATOR] Step 2 FAILED — Brief formatting: {str(e)}")
            raise Exception(
                f"Expert Synthesis Halted at Step 2 (Expert Lens): {str(e)}"
            )

        # ── Step 3: Conditional Dispatch (Safety Gate) ────────────
        if not release_approved:
            print(
                "[ORCHESTRATOR] Release toggle is OFF — brief generated "
                "but NOT dispatched."
            )
            print("--- [ORCHESTRATOR] Expert Synthesis complete (PENDING_RELEASE) ---\n")
            return {
                "dispatch_status": "PENDING_RELEASE",
                "expert_brief": expert_brief,
                "message": "Brief ready for review. Set release_approved=True to dispatch.",
            }

        # Release is approved — send the brief externally
        try:
            dispatch_result = EmailServiceWrapper.send_communication({
                "template_id": "EXPERT_BRIEF_V1",
                "recipient_address": "expert@clinic.local",
                "dynamic_vars": {
                    "patient_id": patient_id,
                    "brief_body": expert_brief["brief_text"],
                },
            })
            print("[ORCHESTRATOR] Step 3 — Brief dispatched externally.")
        except Exception as e:
            print(f"[ORCHESTRATOR] Step 3 FAILED — Dispatch: {str(e)}")
            raise Exception(
                f"Expert Synthesis Halted at Step 3 (Dispatch): {str(e)}"
            )

        print("--- [ORCHESTRATOR] Expert Synthesis complete (DISPATCHED) ---\n")
        return {
            "dispatch_status": "DISPATCHED",
            "expert_brief": expert_brief,
            "dispatch_details": dispatch_result,
        }

    @staticmethod
    def describe_result(result: Dict[str, Any]) -> str:
        brief = result.get("expert_brief", {}).get("brief_text", "")
        return f"The expert brief has been synthesized:\n\n```text\n{brief}\n```"
