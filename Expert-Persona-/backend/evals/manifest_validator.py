"""
evals/manifest_validator.py

Persona Manifest Quality Gate.
Performs both structural and semantic validation of the output.

Structural checks:
- Required fields (identity, communication_style, heuristics, drop_zones)
- Proper data types

Semantic checks (LLM-graded):
- Specificity: Are heuristics general platitudes or specific patterns?
- Framing: Is communication framing clearly defined?
- Differentiability: Is the fallback identity distinct from the expert?

Used in Shadow Mode to auto-grade AI-generated drafts.
"""

import json
import logging
from typing import List, Dict, Any

from pydantic import ValidationError
from core.schemas import PersonaManifest

logger = logging.getLogger(__name__)


class ValidationResult:
    def __init__(self, is_valid: bool, issues: List[str], score: float = 0.0):
        self.is_valid = is_valid
        self.issues = issues
        self.score = score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "issues": self.issues,
            "quality_score": round(self.score, 2)
        }


def validate_manifest_structure(manifest_json: str) -> ValidationResult:
    """Verifies that the JSON matches the PersonaManifest Pydantic schema."""
    try:
        manifest_dict = json.loads(manifest_json)
        PersonaManifest(**manifest_dict)
        return ValidationResult(True, [])
    except json.JSONDecodeError as e:
        return ValidationResult(False, [f"JSON Parse Error: {str(e)}"])
    except ValidationError as e:
        issues = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
        return ValidationResult(False, issues)


def grade_manifest_quality(manifest_dict: dict) -> ValidationResult:
    """
    Performs deterministic quality checks.
    Semantic checks will eventually go through an LLM Judge node.
    """
    issues = []
    score = 100.0

    # 1. Heuristic Count Check
    h_count = len(manifest_dict.get("heuristics", []))
    if h_count < 3:
        issues.append(f"Low Heuristic Count: Only {h_count} found. Minimum 5 recommended.")
        score -= 10 * (3 - h_count)
    elif h_count < 5:
        issues.append(f"Moderate Heuristic Count: {h_count} found. 8-12 is ideal.")
        score -= 5

    # 2. Drop Zone Check
    dz_count = len(manifest_dict.get("drop_zone_triggers", []))
    if dz_count == 0:
        issues.append("Critical: No Expertise Boundaries (Drop Zones) defined.")
        score -= 30
    elif dz_count < 3:
        issues.append(f"Sparse Drop Zones: Only {dz_count} boundaries identified.")
        score -= 10

    # 3. Tone Specificity
    tones = manifest_dict.get("communication_style", {}).get("tone", [])
    if not tones:
        issues.append("Missing Communication Tone.")
        score -= 10
    elif len(tones) < 2:
        issues.append("Under-defined Tone: Only 1 characteristic found.")
        score -= 5

    # 4. Framing Check
    framing = manifest_dict.get("communication_style", {}).get("preferred_framing", "")
    if "not determined" in framing.lower() or not framing:
        issues.append("Missing Communication Framing.")
        score -= 15

    return ValidationResult(len(issues) < 2, issues, max(0, score))


async def run_semantic_eval(manifest_dict: dict, llm: Any) -> Dict[str, Any]:
    """
    LLM-based semantic quality assessment.
    Checks if the heuristics 'feel' like they belong to the expert.
    """
    # PROMPT: "Analyze these heuristics. Are they generic AI advice or expert-specific?"
    # Implementation planned for Stage 4 implementation pass.
    pass
