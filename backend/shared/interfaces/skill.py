"""
shared/interfaces/skill.py

SOLID — Single Responsibility + Open/Closed + Interface Segregation
---------------------------------------------------------------------
Two-tier skill architecture:

  BaseSkill       → raw capability (send email, search KB, draft text)
  FunctionalSkill → expert-contextualized execution (notify a student
                    about their missed assignment, in the doctor's tone,
                    grounded in retrieved context)

New base capabilities = new BaseSkill subclass.
New expert actions    = new FunctionalSkill subclass.
Neither changes the other.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class SkillParams:
    """Input to any skill execution."""
    raw_params: dict = field(default_factory=dict)   # Caller-supplied parameters
    persona_context: Optional[dict] = None           # Injected PersonaManifest fields
    retrieved_cases: Optional[list] = None           # Injected RAG context


@dataclass
class SkillResult:
    """Output of any skill execution."""
    success: bool
    output: Any                         # The actual result (sent email, drafted text, etc.)
    skill_id: str
    error_message: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class BaseSkill(ABC):
    """
    Raw capability — no expert context, no persona, no domain rules.
    This is pure infrastructure: "I can send an email."

    Concrete implementations live in: skills/base/
    """

    @abstractmethod
    def execute(self, params: SkillParams) -> SkillResult:
        """
        Execute the raw capability.
        Must be idempotent where possible.
        Must NEVER raise — return SkillResult(success=False, ...) on failure.
        """

    @abstractmethod
    def get_skill_id(self) -> str:
        """Unique slug. e.g. 'send_email', 'search_kb', 'draft_text'"""

    @abstractmethod
    def get_description(self) -> str:
        """Human-readable description for skill registry / discovery."""


class FunctionalSkill(BaseSkill, ABC):
    """
    Expert-contextualized execution — wraps a BaseSkill and injects:
      - PersonaManifest → tone, heuristics, drop_zone_triggers
      - Retrieved Master Cases → domain-specific grounding
      - Domain rules → immutable constraints from DomainAdapter

    "I can send THIS expert's email to THIS person about THIS event."

    Concrete implementations live in: skills/functional/
    """

    def __init__(self, base_skill: BaseSkill):
        """
        DIP: FunctionalSkill depends on BaseSkill abstraction, not a concrete class.
        Inject any BaseSkill at construction time.
        """
        self._base = base_skill

    @property
    def base_skill(self) -> BaseSkill:
        return self._base

    @abstractmethod
    def _enrich_params(self, params: SkillParams) -> SkillParams:
        """
        Apply persona framing, retrieved context, and domain rules to params
        BEFORE delegating to the base skill.
        """

    @abstractmethod
    def _post_process(self, result: SkillResult, params: SkillParams) -> SkillResult:
        """
        Apply persona communication style to the raw output
        AFTER the base skill executes.
        """

    def execute(self, params: SkillParams) -> SkillResult:
        """
        Template method — fixed execution order:
        1. Check drop_zone_triggers (refuse if out of scope)
        2. Enrich params with persona + context
        3. Delegate to base skill
        4. Post-process output through persona style
        """
        # Step 1: Drop zone check
        if params.persona_context:
            drop_zones = params.persona_context.get("drop_zone_triggers", [])
            skill_scope = self.get_scope_keywords()
            for trigger in drop_zones:
                if any(kw in trigger.lower() for kw in skill_scope):
                    return SkillResult(
                        success=False,
                        output=None,
                        skill_id=self.get_skill_id(),
                        error_message=f"Out of expert scope: {trigger}",
                    )

        # Step 2: Enrich
        enriched = self._enrich_params(params)

        # Step 3: Delegate
        raw_result = self._base.execute(enriched)

        # Step 4: Post-process
        return self._post_process(raw_result, enriched)

    @abstractmethod
    def get_scope_keywords(self) -> list[str]:
        """
        Keywords that, if found in drop_zone_triggers, will block this skill.
        Example: ["billing", "finance"] would block a billing-related functional skill
        if the expert's drop zone includes financial topics.
        """
