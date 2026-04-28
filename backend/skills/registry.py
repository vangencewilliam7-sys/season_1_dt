"""
skills/registry.py

SOLID — Open/Closed + Single Responsibility
---------------------------------------------
The SkillRegistry is the ONLY place skills are registered.
Adding a new skill = add one line to _build_registry().
Zero changes to callers.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from typing import Dict, Optional
from shared.interfaces.skill import BaseSkill, FunctionalSkill
from skills.base.draft_skill import DraftSkill
from skills.base.notify_skill import NotifySkill
from skills.base.search_kb_skill import SearchKBSkill
from skills.functional.doctor_skills import (
    PatientFollowUpSkill,
    PatientPreCycleInstructionSkill,
    CaseEscalationSkill,
    TreatmentSummaryReportSkill,
    KnowledgeGapFlagSkill,
)


class SkillRegistry:
    """
    Central registry of all available skills.

    Usage:
        registry = SkillRegistry()
        skill = registry.get("doctor_patient_followup")
        result = skill.execute(params)
    """

    def __init__(self, vault_service=None, embedding_service=None):
        self._vault = vault_service
        self._embedder = embedding_service
        self._registry: Dict[str, BaseSkill] = {}
        self._build_registry()

    def _build_registry(self):
        """Register all skills. Add new skills here."""

        # ── Base Skills ──────────────────────────────────────────────────────
        draft = DraftSkill()
        notify = NotifySkill()
        search = SearchKBSkill(
            vault_service=self._vault,
            embedding_service=self._embedder,
        )

        self._register(draft)
        self._register(notify)
        self._register(search)

        # ── Doctor / Healthcare Functional Skills ────────────────────────────
        self._register(PatientFollowUpSkill(base_skill=notify))
        self._register(PatientPreCycleInstructionSkill(base_skill=notify))
        self._register(CaseEscalationSkill(base_skill=notify))
        self._register(TreatmentSummaryReportSkill(base_skill=draft))
        self._register(KnowledgeGapFlagSkill(base_skill=notify))

    def _register(self, skill: BaseSkill):
        self._registry[skill.get_skill_id()] = skill

    def get(self, skill_id: str) -> Optional[BaseSkill]:
        """Return the skill by ID, or None if not found."""
        return self._registry.get(skill_id)

    def list_all(self) -> Dict[str, str]:
        """Return {skill_id: description} for all registered skills."""
        return {
            skill_id: skill.get_description()
            for skill_id, skill in self._registry.items()
        }

    def list_functional(self) -> Dict[str, str]:
        """Return only functional (expert-contextualized) skills."""
        return {
            skill_id: skill.get_description()
            for skill_id, skill in self._registry.items()
            if isinstance(skill, FunctionalSkill)
        }
