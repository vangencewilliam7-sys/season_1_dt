"""
orchestrator.py — Backward-Compatible Re-Export Hub
=====================================================
DEPRECATED: Do not add new functional skills here.
Instead, create a class extending BaseFunctionalSkill in the
domain-specific directory (e.g., functional/healthcare/).

This file delegates to the skill_router for backward compatibility.
"""
from app.skills.functional.skill_router import execute_skill


class FunctionalOrchestrator:
    """
    DEPRECATED compatibility shim.
    Delegates all execution to the auto-discovery skill_router.
    """

    @staticmethod
    def execute_pre_op_gatekeeper(payload):
        return execute_skill("SKL_PRE_OP_GATEKEEPER", payload)

    @staticmethod
    def execute_expert_synthesis(payload):
        return execute_skill("SKL_EXPERT_SYNTHESIS", payload)

    @staticmethod
    def execute_baseline_vigilance(payload):
        return execute_skill("SKL_BASELINE_VIGILANCE", payload)
