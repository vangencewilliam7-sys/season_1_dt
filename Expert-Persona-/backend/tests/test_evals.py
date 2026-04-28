"""
tests/test_evals.py

Unit tests for the Manifest Validator (Phase 4).
Verifies that the quality gate correctly identifies low-quality
or structurally invalid Persona Manifests.
"""

import json
import pytest
from evals.manifest_validator import validate_manifest_structure, grade_manifest_quality


def test_validator_detects_structural_issues():
    # Missing required 'identity' field
    invalid_manifest = {
        "expert_id": "550e8400-e29b-41d4-a716-446655440000",
        "extracted_at": "2026-04-22T12:00:00Z",
        "heuristics": []
    }
    
    result = validate_manifest_structure(json.dumps(invalid_manifest))
    assert result.is_valid is False
    assert any("identity" in issue for issue in result.issues)


def test_validator_grades_low_quality_manifests():
    # A manifest with very few heuristics and no drop zones
    low_quality = {
        "identity": {"name": "Test", "role": "Dev", "domain": "IT"},
        "communication_style": {"tone": ["professional"], "verbosity": "concise", "preferred_framing": "Direct"},
        "heuristics": [{"trigger": "X", "decision": "Y", "reasoning": "Z"}], # Only 1
        "drop_zone_triggers": [] # Empty
    }
    
    result = grade_manifest_quality(low_quality)
    assert result.is_valid is False
    assert result.score < 70
    assert any("No Expertise Boundaries" in issue for issue in result.issues)
    assert any("Low Heuristic Count" in issue for issue in result.issues)


def test_validator_approves_high_quality_manifests():
    high_quality = {
        "identity": {"name": "Senior Architect", "role": "Principal", "domain": "tech"},
        "communication_style": {
            "tone": ["analytical", "assertive"],
            "verbosity": "detailed",
            "preferred_framing": "Risk-first evaluation"
        },
        "heuristics": [
            {"trigger": "T1", "decision": "D1", "reasoning": "R1"},
            {"trigger": "T2", "decision": "D2", "reasoning": "R2"},
            {"trigger": "T3", "decision": "D3", "reasoning": "R3"},
            {"trigger": "T4", "decision": "D4", "reasoning": "R4"},
            {"trigger": "T5", "decision": "D5", "reasoning": "R5"}
        ],
        "drop_zone_triggers": ["Z1", "Z2", "Z3"]
    }
    
    result = grade_manifest_quality(high_quality)
    assert result.is_valid is True
    assert result.score > 90
