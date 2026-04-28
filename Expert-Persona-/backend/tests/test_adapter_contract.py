"""
tests/test_adapter_contract.py

Validates that ANY DomainAdapter implementation is framework-compliant.
Run this test against every new adapter before deploying.

Usage:
    pytest tests/test_adapter_contract.py               # tests GenericAdapter
    pytest tests/test_adapter_contract.py -v            # verbose
"""

import pytest
from adapters._reference_impl.generic_adapter import GenericAdapter
from adapters.recruiting.recruiting_adapter import RecruitingAdapter
from adapters.healthcare.healthcare_adapter import HealthcareAdapter
from adapters.tech_consulting.tech_consulting_adapter import TechConsultingAdapter
from adapters.base_adapter import DomainAdapter


# ── Parameterise with all adapters you want to validate ──────────────────────
ADAPTERS_TO_TEST = [
    GenericAdapter(),
    RecruitingAdapter(),
    HealthcareAdapter(),
    TechConsultingAdapter(),
]


@pytest.mark.parametrize("adapter", ADAPTERS_TO_TEST)
class TestAdapterContract:
    """
    Contract tests — every adapter MUST pass ALL of these.
    Failing any test = the adapter is not framework-compliant.
    """

    def test_is_domain_adapter_subclass(self, adapter):
        """Adapter must extend DomainAdapter."""
        assert isinstance(adapter, DomainAdapter)

    def test_get_domain_id_returns_non_empty_string(self, adapter):
        """Domain ID must be a non-empty string slug."""
        domain_id = adapter.get_domain_id()
        assert isinstance(domain_id, str)
        assert len(domain_id.strip()) > 0
        assert " " not in domain_id, "Domain ID should be a slug (no spaces)"

    def test_get_immutable_rules_returns_non_empty_string(self, adapter):
        """Immutable rules must be defined — cannot be empty."""
        rules = adapter.get_immutable_rules()
        assert isinstance(rules, str)
        assert len(rules.strip()) > 0, "Immutable rules cannot be empty"

    def test_get_fallback_identity_returns_required_keys(self, adapter):
        """Fallback identity must have role, tone, and action keys."""
        fallback = adapter.get_fallback_identity()
        assert isinstance(fallback, dict)
        assert "role" in fallback, "Fallback identity must have 'role'"
        assert "tone" in fallback, "Fallback identity must have 'tone'"
        assert "action" in fallback, "Fallback identity must have 'action'"
        assert all(isinstance(v, str) for v in fallback.values()), \
            "All fallback identity values must be strings"

    def test_get_extraction_context_returns_non_empty_string(self, adapter):
        """Extraction context must guide the journalist — cannot be empty."""
        context = adapter.get_extraction_context()
        assert isinstance(context, str)
        assert len(context.strip()) > 0, "Extraction context cannot be empty"

    def test_immutable_rules_cannot_be_overridden_by_persona_framing(self, adapter):
        """
        Safety test: verify that immutable rules contain no override instructions.
        Rules must be directives, not conditionals that can be bypassed.
        """
        rules = adapter.get_immutable_rules().lower()
        bypass_phrases = [
            "unless instructed",
            "unless told",
            "you may override",
            "can be overridden",
            "if the persona says",
        ]
        for phrase in bypass_phrases:
            assert phrase not in rules, (
                f"Immutable rules contain potential bypass phrase: '{phrase}'. "
                "Rules must be absolute, not conditional."
            )
