"""
schemas/__init__.py — Skill Schema Package
============================================
Exports the shared base models and the unified SKILL_REGISTRY
which merges all domain-specific registries.
"""
from .base import SkillMetadata, SkillRequest, SkillResponse

# Domain-specific registries are imported by validation.py directly.
# This __init__ only exposes the shared base models.

__all__ = ["SkillMetadata", "SkillRequest", "SkillResponse"]
