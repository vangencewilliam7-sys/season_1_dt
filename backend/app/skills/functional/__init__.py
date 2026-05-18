"""
functional/__init__.py — Functional Skills Package
=====================================================
Exports the skill_router (primary) and backward-compat orchestrator.
Domain sub-packages are auto-discovered by skill_router — no imports needed here.
"""
from .skill_router import execute_skill, describe_result, list_skills
from .skill_router import FUNCTIONAL_SKILL_REGISTRY, BASE_WRAPPER_REGISTRY

# Backward-compatibility
from .orchestrator import FunctionalOrchestrator

__all__ = [
    "execute_skill",
    "describe_result",
    "list_skills",
    "FUNCTIONAL_SKILL_REGISTRY",
    "BASE_WRAPPER_REGISTRY",
    "FunctionalOrchestrator",
]
