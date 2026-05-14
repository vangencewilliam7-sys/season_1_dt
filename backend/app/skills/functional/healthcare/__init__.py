"""
healthcare/__init__.py — Healthcare Functional Skills Package
==============================================================
Dev A (Healthcare) owns this directory.

ADDING A NEW HEALTHCARE FUNCTIONAL SKILL:
    1. Create a new .py file in this directory (e.g., new_skill.py)
    2. Define a class with a static execute() method
    3. Register the skill_name in skills/schemas/healthcare.py
    4. Wire the routing in the skill executor (if not auto-routed)
"""
from .pre_op_gatekeeper import PreOpGatekeeper
from .expert_synthesis import ExpertSynthesis
from .baseline_vigilance import BaselineVigilance

__all__ = ["PreOpGatekeeper", "ExpertSynthesis", "BaselineVigilance"]
