"""
base_skill.py — Abstract Functional Skill Contract
=====================================================
Every functional skill class MUST extend this interface.

The skill_router.py auto-discovers all BaseFunctionalSkill subclasses
across all domain subdirectories. To register a new functional skill:

    1. Create a class extending BaseFunctionalSkill
    2. Implement skill_name() and execute()
    3. Optionally override describe_result() for chat-friendly output
    4. Done — skill_router.py finds it automatically.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseFunctionalSkill(ABC):
    """
    Abstract base class for all functional skills.
    Each subclass handles exactly one skill_name string.
    """

    @staticmethod
    @abstractmethod
    def skill_name() -> str:
        """
        Returns the exact skill_name string this class handles.
        Must match the key used in the domain's SKILL_REGISTRY.
        Example: 'SKL_PRE_OP_GATEKEEPER'
        """
        ...

    @staticmethod
    @abstractmethod
    def execute(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the skill with a validated payload dict.
        Returns a result dict.
        """
        ...

    @staticmethod
    def describe_result(result: Dict[str, Any]) -> str:
        """
        Human-readable description of the result for chat responses.
        Override in subclasses for custom formatting.
        Default returns a generic message.
        """
        return "Action completed successfully."
