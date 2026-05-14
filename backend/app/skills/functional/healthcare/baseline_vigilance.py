"""
baseline_vigilance.py — SKL_BASELINE_VIGILANCE Functional Skill
=================================================================
Real-time vitals extraction + baseline threshold comparison.
Composes: ACT_VISION_OCR (with threshold evaluation logic)

Owner: Dev A (Healthcare)
"""
from typing import Dict, Any
from app.skills.functional.base_skill import BaseFunctionalSkill
from app.skills.wrappers.clinical_services import ClinicalServicesWrapper


class BaselineVigilance(BaseFunctionalSkill):

    @staticmethod
    def skill_name() -> str:
        return "SKL_BASELINE_VIGILANCE"

    @staticmethod
    def execute(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrates SKL_BASELINE_VIGILANCE
        Step 1: Extract current vitals via ACT_VISION_OCR
        Step 2: Compare against patient-specific baseline thresholds
        Step 3: Return verdict — ALL_NORMAL or BREACH_DETECTED
        """
        print("\n--- [ORCHESTRATOR] Starting SKL_BASELINE_VIGILANCE ---")

        patient_id = str(payload["patient_id"])
        thresholds = payload["baseline_thresholds"]

        # ── Step 1: Vitals Extraction via OCR ─────────────────────
        try:
            ocr_result = ClinicalServicesWrapper.extract_vitals({
                "extraction_type": "VITALS",
                "image_url": payload.get("image_url"),
            })
            vitals_numeric = ocr_result.get("vitals_numeric", {})
            print(f"[ORCHESTRATOR] Step 1 — Vitals extracted: {vitals_numeric}")
        except Exception as e:
            print(f"[ORCHESTRATOR] Step 1 FAILED — Vitals OCR: {str(e)}")
            raise Exception(
                f"Baseline Vigilance Halted at Step 1 (Vitals OCR): {str(e)}"
            )

        # ── Step 2: Threshold Comparison ──────────────────────────
        try:
            comparison = ClinicalServicesWrapper.compare_vitals_to_baseline(
                vitals_numeric, thresholds
            )
            breaches = comparison.get("breaches", [])
            print(
                f"[ORCHESTRATOR] Step 2 — Comparison complete. "
                f"Checked {comparison['total_checked']} vitals, "
                f"found {len(breaches)} breach(es)."
            )
        except Exception as e:
            print(f"[ORCHESTRATOR] Step 2 FAILED — Threshold comparison: {str(e)}")
            raise Exception(
                f"Baseline Vigilance Halted at Step 2 (Comparison): {str(e)}"
            )

        # ── Step 3: Verdict ───────────────────────────────────────
        if not breaches:
            print("--- [ORCHESTRATOR] Baseline Vigilance complete (ALL_NORMAL) ---\n")
            return {
                "vigilance_status": "ALL_NORMAL",
                "patient_id": patient_id,
                "vitals_snapshot": ocr_result.get("vitals", {}),
                "message": "All vitals within baseline thresholds.",
            }

        print("--- [ORCHESTRATOR] Baseline Vigilance complete (BREACH_DETECTED) ---\n")
        return {
            "vigilance_status": "BREACH_DETECTED",
            "patient_id": patient_id,
            "vitals_snapshot": ocr_result.get("vitals", {}),
            "breaches": breaches,
            "total_checked": comparison["total_checked"],
            "message": f"{len(breaches)} vital(s) outside baseline range.",
        }

    @staticmethod
    def describe_result(result: Dict[str, Any]) -> str:
        status = result.get("vigilance_status", "UNKNOWN")
        msg = result.get("message", "")
        return f"Baseline vigilance monitoring is complete. Status: **{status}**\n{msg}"
