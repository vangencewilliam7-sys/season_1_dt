"""
pre_op_gatekeeper.py — SKL_PRE_OP_GATEKEEPER Functional Skill
===============================================================
Multi-step pre-surgery readiness saga.
Composes: ACT_CHECKLIST_VERIFY + ACT_VISION_OCR

Owner: Dev A (Healthcare)
"""
from typing import Dict, Any
from app.skills.functional.base_skill import BaseFunctionalSkill
from app.skills.wrappers.clinical_services import ClinicalServicesWrapper


class PreOpGatekeeper(BaseFunctionalSkill):

    @staticmethod
    def skill_name() -> str:
        return "SKL_PRE_OP_GATEKEEPER"

    @staticmethod
    def execute(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrates SKL_PRE_OP_GATEKEEPER
        Step 1: Verify checklist
        Step 2: Extract vitals
        Returns Readiness Verdict
        """
        print("\n--- [ORCHESTRATOR] Starting SKL_PRE_OP_GATEKEEPER ---")

        # Step 1: Checklist Audit
        try:
            audit_result = ClinicalServicesWrapper.verify_checklist({
                "patient_id": payload["patient_id"],
                "required_documents": payload["required_documents"]
            })
            print("[ORCHESTRATOR] Checklist passed.")
        except Exception as e:
            print(f"[ORCHESTRATOR] Checklist failed: {str(e)}")
            raise Exception(f"Gatekeeper Halted at Step 1 (Audit): {str(e)}")

        # Step 2: Vitals Extraction
        try:
            vitals_result = ClinicalServicesWrapper.extract_vitals({
                "extraction_type": "VITALS"
            })
            print("[ORCHESTRATOR] Vitals extracted successfully.")
        except Exception as e:
            print(f"[ORCHESTRATOR] Vitals extraction failed: {str(e)}")
            raise Exception(f"Gatekeeper Halted at Step 2 (Vitals OCR): {str(e)}")

        # Final Verdict Synthesis
        print("--- [ORCHESTRATOR] Gatekeeper passed successfully! ---\n")
        return {
            "readiness_verdict": "CLEARED_FOR_SURGERY",
            "audit_details": audit_result,
            "vitals_snapshot": vitals_result
        }

    @staticmethod
    def describe_result(result: Dict[str, Any]) -> str:
        verdict = result.get("readiness_verdict", "UNKNOWN")
        return f"The pre-op readiness check is complete. Verdict: **{verdict}**"
