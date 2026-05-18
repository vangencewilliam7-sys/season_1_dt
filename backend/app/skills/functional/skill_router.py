"""
skill_router.py — Unified Skill Execution Router (Full Auto-Discovery)
========================================================================
Replaces ALL if/elif chains in routes.py and skill_executor.py.

Auto-discovers:
    1. Functional skills (BaseFunctionalSkill subclasses in functional/{domain}/)
    2. Base skill wrappers (BaseSkillWrapper subclasses in wrappers/)

To add a new skill of ANY type in ANY domain:
    - Just create the class in the right directory
    - It appears here automatically
    - NO EDITS TO THIS FILE OR ANY SHARED FILE
"""
import importlib
import inspect
import pathlib
from typing import Dict, Any, Optional, Type

from app.skills.functional.base_skill import BaseFunctionalSkill
from app.skills.wrappers.base_wrapper import BaseSkillWrapper


# ── Auto-Discovery: Functional Skills ────────────────────────────────────────

def _discover_functional_skills() -> Dict[str, Type[BaseFunctionalSkill]]:
    """
    Scan all domain subdirectories in functional/ for BaseFunctionalSkill
    subclasses. Each skill class declares its own skill_name().

    Directory structure scanned:
        functional/healthcare/*.py
        functional/it/*.py
        functional/education/*.py
        functional/presales/*.py
        functional/<any_future_domain>/*.py
    """
    registry: Dict[str, Type[BaseFunctionalSkill]] = {}
    func_dir = pathlib.Path(__file__).parent

    skip_files = {"__init__.py", "base_skill.py", "skill_router.py", "orchestrator.py"}

    for domain_dir in sorted(func_dir.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith("_"):
            continue

        for py_file in sorted(domain_dir.glob("*.py")):
            if py_file.name in skip_files or py_file.name.startswith("_"):
                continue

            module_path = f"app.skills.functional.{domain_dir.name}.{py_file.stem}"
            try:
                module = importlib.import_module(module_path)
            except Exception as e:
                print(f"[SKILL_ROUTER] Warning: Failed to import {module_path}: {e}")
                continue

            for _, cls in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(cls, BaseFunctionalSkill)
                    and cls is not BaseFunctionalSkill
                ):
                    name = cls.skill_name()
                    registry[name] = cls

    return registry


# ── Auto-Discovery: Base Skill Wrappers ──────────────────────────────────────

def _discover_base_wrappers() -> Dict[str, Type[BaseSkillWrapper]]:
    """
    Scan all .py files in wrappers/ for BaseSkillWrapper subclasses.
    Each wrapper declares SKILL_NAMES = ["skill_a", "skill_b"].
    """
    registry: Dict[str, Type[BaseSkillWrapper]] = {}
    wrappers_dir = pathlib.Path(__file__).parent.parent / "wrappers"

    skip_files = {"__init__.py", "base_wrapper.py", "resilience.py"}

    for py_file in sorted(wrappers_dir.glob("*.py")):
        if py_file.name in skip_files or py_file.name.startswith("_"):
            continue

        module_path = f"app.skills.wrappers.{py_file.stem}"
        try:
            module = importlib.import_module(module_path)
        except Exception as e:
            print(f"[SKILL_ROUTER] Warning: Failed to import {module_path}: {e}")
            continue

        for _, cls in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(cls, BaseSkillWrapper)
                and cls is not BaseSkillWrapper
                and hasattr(cls, "SKILL_NAMES")
            ):
                for skill_name in cls.SKILL_NAMES:
                    registry[skill_name] = cls

    return registry


# ── Build registries once at import time ─────────────────────────────────────
FUNCTIONAL_SKILL_REGISTRY: Dict[str, Type[BaseFunctionalSkill]] = _discover_functional_skills()
BASE_WRAPPER_REGISTRY: Dict[str, Type[BaseSkillWrapper]] = _discover_base_wrappers()


def execute_skill(skill_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Universal skill executor. Routes to the correct handler automatically.

    Priority:
        1. Functional skills (BaseFunctionalSkill subclasses) — checked first
        2. Base wrappers (BaseSkillWrapper subclasses) — fallback
        3. Generic stub — if neither is found

    Args:
        skill_name: The exact skill name string (e.g., 'SKL_PRE_OP_GATEKEEPER')
        payload: The validated payload dict

    Returns:
        Result dict from the skill execution.
    """
    # Try functional skills first (they compose base skills internally)
    func_cls = FUNCTIONAL_SKILL_REGISTRY.get(skill_name)
    if func_cls:
        return func_cls.execute(payload)

    # Try base wrappers
    wrapper_cls = BASE_WRAPPER_REGISTRY.get(skill_name)
    if wrapper_cls:
        return wrapper_cls.execute(skill_name, payload)

    # Generic fallback for unrouted skills
    return {
        "message": f"Successfully executed generic {skill_name}",
        "processed_data": payload
    }


def describe_result(skill_name: str, result: Dict[str, Any]) -> str:
    """
    Get a human-readable description of the result for chat responses.
    Delegates to the skill's describe_result() if available.
    """
    # Try functional skill
    func_cls = FUNCTIONAL_SKILL_REGISTRY.get(skill_name)
    if func_cls:
        return func_cls.describe_result(result)

    # Try base wrapper
    wrapper_cls = BASE_WRAPPER_REGISTRY.get(skill_name)
    if wrapper_cls:
        return wrapper_cls.describe_result(skill_name, result)

    # Generic
    return f"Action {skill_name} completed."


def list_skills() -> Dict[str, dict]:
    """
    Returns a summary of all registered skills.
    Useful for debug endpoints and admin UIs.
    """
    skills = {}
    for name in FUNCTIONAL_SKILL_REGISTRY:
        skills[name] = {"type": "functional", "domain": "auto-discovered"}
    for name in BASE_WRAPPER_REGISTRY:
        if name not in skills:
            skills[name] = {"type": "base_wrapper", "domain": "shared"}
    return skills
