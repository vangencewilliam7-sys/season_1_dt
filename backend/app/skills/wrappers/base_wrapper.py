"""
base_wrapper.py — Abstract Base Skill Wrapper Contract
========================================================
Every base skill wrapper (calendar, email, CRM, etc.) MAY extend this
interface to participate in auto-discovery routing.

Base skills are atomic, domain-agnostic operations. They are auto-discovered
by the skill_router if they declare SKILL_NAMES.

ADDING A NEW BASE SKILL WRAPPER:
    1. Create a class extending BaseSkillWrapper
    2. Set SKILL_NAMES to the list of skill_name strings it handles
    3. Implement execute() which routes to the correct internal method
    4. Done — the skill_router finds it automatically.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseSkillWrapper(ABC):
    """
    Abstract base class for auto-discoverable base skill wrappers.
    Each subclass declares the skill_name strings it handles.
    """

    # Override this in subclasses with the skill names this wrapper handles
    SKILL_NAMES: List[str] = []

    @staticmethod
    @abstractmethod
    def execute(skill_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the named base skill with the given payload.
        The skill_name is passed in case the wrapper handles multiple skills.
        """
        ...

    @staticmethod
    def describe_result(skill_name: str, result: Dict[str, Any]) -> str:
        """
        Human-readable result description for chat responses.
        Override for custom formatting.
        """
        return f"Action '{skill_name}' completed successfully."
