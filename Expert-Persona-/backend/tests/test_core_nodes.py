"""
tests/test_core_nodes.py

Unit tests for Layer 1 extraction nodes.
Uses GenericAdapter and mock LLM — no real API calls, no real documents.

These tests verify:
- Node input/output contracts
- Error handling (bad LLM responses, empty documents)
- State threading between nodes
"""

import json
import pytest
from unittest.mock import MagicMock

from core.schemas import ExtractionState
from core.nodes.ingestion_node import ingestion_node
from core.nodes.journalist_node import journalist_node
from core.nodes.compiler_node import compiler_node
from adapters._reference_impl.generic_adapter import GenericAdapter


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def adapter():
    return GenericAdapter()


@pytest.fixture
def sample_documents():
    return [
        {
            "source": "test/expert_cv.txt",
            "content": (
                "Dr. Jane Smith has 15 years of experience in software architecture. "
                "She prefers event-driven systems and always insists on horizontal scalability. "
                "She avoids monolithic designs and has written extensively on microservices patterns. "
                "Known for asking hard questions about failure modes before approving any design."
            ),
            "metadata": {"type": "cv", "expert_id": "test-expert-001"},
        },
        {
            "source": "test/case_study_1.txt",
            "content": (
                "Case: E-commerce platform scaling challenge. "
                "Jane recommended event sourcing over traditional CRUD due to audit requirements. "
                "She identified that the team had underestimated message broker complexity. "
                "Decision: Decompose user service first, then payments. Defer search service to Phase 2."
            ),
            "metadata": {"type": "master_case", "expert_id": "test-expert-001"},
        }
    ]


@pytest.fixture
def base_state(sample_documents) -> ExtractionState:
    return ExtractionState(
        expert_id="test-expert-001",
        domain="generic",
        documents=sample_documents,
        behavioral_hypotheses=[],
        journalist_findings={},
        final_manifest=None,
        error=None,
        identity_override={"name": "Dr. Jane Smith", "role": "Principal Architect"},
    )


def make_mock_llm(response: str):
    """Create a mock LLM that returns the given string."""
    mock = MagicMock()
    mock.chat.return_value = response
    mock.get_model_id.return_value = "mock-llm"
    return mock


# ── Ingestion Node Tests ──────────────────────────────────────────────────────

class TestIngestionNode:

    def test_extracts_hypotheses_from_documents(self, base_state, adapter):
        mock_response = json.dumps({
            "hypotheses": [
                "Prefers event-driven architecture over CRUD-based systems when audit trails are required",
                "Consistently decomposes services in order of business risk, not technical complexity",
            ],
            "observed_knowledge_gaps": ["mobile development", "machine learning infrastructure"]
        })
        llm = make_mock_llm(mock_response)

        result = ingestion_node(base_state, llm=llm, adapter=adapter)

        assert len(result["behavioral_hypotheses"]) == 2
        assert result["error"] is None
        assert "preliminary_drop_zones" in result["journalist_findings"]

    def test_handles_empty_documents(self, base_state, adapter):
        state = {**base_state, "documents": []}
        llm = make_mock_llm("")

        result = ingestion_node(state, llm=llm, adapter=adapter)

        assert result["error"] is not None
        assert "No documents" in result["error"]

    def test_handles_invalid_json_response(self, base_state, adapter):
        llm = make_mock_llm("This is not JSON at all.")

        result = ingestion_node(base_state, llm=llm, adapter=adapter)

        assert result["error"] is not None
        assert "JSON parse error" in result["error"]


# ── Journalist Node Tests ─────────────────────────────────────────────────────

class TestJournalistNode:

    @pytest.fixture
    def state_after_ingestion(self, base_state) -> ExtractionState:
        return {
            **base_state,
            "behavioral_hypotheses": [
                "Prefers event-driven architecture when audit trails are required",
                "Decomposes services by business risk order",
            ],
            "journalist_findings": {"preliminary_drop_zones": ["mobile development"]},
        }

    def test_produces_journalist_findings(self, state_after_ingestion, adapter):
        questions_response = json.dumps({
            "validation_questions": [
                {
                    "question": "You're designing an e-commerce system. The team wants CRUD. What do you say?",
                    "tests_hypothesis": "Event-driven preference",
                    "expected_reveal": "Reasoning about audit requirements"
                }
            ],
            "boundary_questions": [
                {
                    "question": "How would you optimise a TensorFlow training pipeline?",
                    "boundary_area": "ML infrastructure"
                }
            ]
        })
        answers_response = json.dumps({
            "answered_questions": [
                {
                    "question": "You're designing an e-commerce system...",
                    "answer": "I'd push for event sourcing because we'll need full audit trails.",
                    "confidence": "high",
                    "evidence_source": "test/case_study_1.txt",
                    "is_outside_scope": False
                }
            ],
            "confirmed_heuristics": [
                {
                    "trigger": "When a system requires audit trails or compliance logging",
                    "decision": "Recommend event sourcing over traditional CRUD",
                    "reasoning": "CRUD loses history; event sourcing is the definitive record"
                }
            ],
            "confirmed_drop_zones": ["ML infrastructure", "mobile development"],
            "communication_style": {
                "tone": ["direct", "analytical"],
                "verbosity": "concise",
                "preferred_framing": "Leads with risk identification before recommending solutions"
            }
        })

        call_count = [0]
        def mock_chat(messages, **kwargs):
            call_count[0] += 1
            return questions_response if call_count[0] == 1 else answers_response

        llm = MagicMock()
        llm.chat.side_effect = mock_chat

        result = journalist_node(state_after_ingestion, llm=llm, adapter=adapter)

        assert result["error"] is None
        assert len(result["journalist_findings"]["confirmed_heuristics"]) == 1
        assert len(result["journalist_findings"]["confirmed_drop_zones"]) == 2
        assert "communication_style" in result["journalist_findings"]

    def test_handles_no_hypotheses(self, base_state, adapter):
        llm = make_mock_llm("")
        result = journalist_node(base_state, llm=llm, adapter=adapter)
        assert result["error"] is not None


# ── Compiler Node Tests ───────────────────────────────────────────────────────

class TestCompilerNode:

    @pytest.fixture
    def state_after_journalist(self, base_state) -> ExtractionState:
        return {
            **base_state,
            "behavioral_hypotheses": ["hypothesis 1"],
            "journalist_findings": {
                "confirmed_heuristics": [
                    {
                        "trigger": "When audit trail is required",
                        "decision": "Use event sourcing",
                        "reasoning": "CRUD loses history"
                    },
                    {
                        "trigger": "When decomposing services",
                        "decision": "Start with highest business risk service",
                        "reasoning": "Reduces risk of costly late-stage rework"
                    },
                    {
                        "trigger": "Before approving any design",
                        "decision": "Ask about failure modes first",
                        "reasoning": "Failure paths are harder to retrofit than features"
                    }
                ],
                "confirmed_drop_zones": ["ML infrastructure", "mobile development"],
                "communication_style": {
                    "tone": ["direct", "analytical"],
                    "verbosity": "concise",
                    "preferred_framing": "Leads with risk before solution"
                }
            }
        }

    def test_compiles_valid_manifest(self, state_after_journalist, adapter):
        result = compiler_node(state_after_journalist, adapter=adapter)

        assert result["error"] is None
        assert result["final_manifest"] is not None

        manifest = json.loads(result["final_manifest"])
        assert manifest["shadow_approved"] is False
        assert len(manifest["heuristics"]) == 3
        assert len(manifest["drop_zone_triggers"]) == 2
        assert manifest["identity"]["domain"] == "generic"

    def test_manifest_is_not_approved_by_default(self, state_after_journalist, adapter):
        result = compiler_node(state_after_journalist, adapter=adapter)
        manifest = json.loads(result["final_manifest"])
        assert manifest["shadow_approved"] is False

    def test_flags_insufficient_heuristics(self, base_state, adapter):
        state = {
            **base_state,
            "journalist_findings": {
                "confirmed_heuristics": [
                    {"trigger": "X", "decision": "Y", "reasoning": "Z"}
                ],  # Only 1 — below minimum of 3
                "confirmed_drop_zones": ["topic A"],
                "communication_style": {
                    "tone": ["direct"],
                    "verbosity": "concise",
                    "preferred_framing": "Direct"
                }
            }
        }
        result = compiler_node(state, adapter=adapter)
        # Should still compile, but flag the issue
        assert result["error"] is None
        assert len(result.get("compilation_issues", [])) > 0
