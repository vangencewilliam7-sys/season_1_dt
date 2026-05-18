"""
presales/__init__.py — Pre-Sales Functional Skills Package
============================================================
Dev D (Pre-Sales) owns this directory.

ADDING A NEW PRE-SALES FUNCTIONAL SKILL:
    1. Create a new .py file in this directory (e.g., tech_stack_inference.py)
    2. Define a class extending BaseFunctionalSkill
    3. Implement skill_name(), execute(), and optionally describe_result()
    4. Add the payload schema to skills/schemas/presales.py
    5. Done — skill_router.py discovers it automatically.
"""
# TODO: Dev D — import your functional skill classes here as you create them.
# Example:
# from .tech_stack_inference import TechStackInference
# from .discovery_brief import DiscoveryBrief
# from .reference_match import ReferenceMatch

__all__ = []
