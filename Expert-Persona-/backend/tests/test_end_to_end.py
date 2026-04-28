"""
tests/test_end_to_end.py

High-level integration test for the full extraction pipeline.
Exercises the LangGraph flow from raw documents to final PersonaManifest.
Uses mock LLM providers to avoid external API calls.
"""

import json
import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from core.graph import build_extraction_graph, create_initial_state
from adapters._reference_impl.generic_adapter import GenericAdapter
from runtime.readers.base_reader import Document


@pytest.fixture
def mock_ingestion_response():
    return json.dumps({
        "hypotheses": [
            "Analytical and data-driven recruiter who prioritizes technical depth.",
            "Conservative approach to candidate salary expectations."
        ],
        "observed_knowledge_gaps": ["executive search", "legal compliance"]
    })


@pytest.fixture
def mock_journalist_questions_response():
    return json.dumps({
        "validation_questions": [
            {
                "question": "Scenario: Candidate has great skills but poor communication. What do you do?",
                "tests_hypothesis": "Analytical depth priority",
                "expected_reveal": "Trade-off logic"
            }
        ],
        "boundary_questions": [
            {
                "question": "How do you handle a CFO search?",
                "boundary_area": "executive search"
            }
        ]
    })


@pytest.fixture
def mock_journalist_answers_response():
    return json.dumps({
        "answered_questions": [
            {
                "question": "Scenario: Candidate has great skills but poor communication...",
                "answer": "I focus on the technical evidence first. Poor communication is a yellow flag, not red.",
                "confidence": "high",
                "evidence_source": "case_1.txt",
                "is_outside_scope": False
            }
        ],
        "confirmed_heuristics": [
            {
                "trigger": "Candidate has strong technical skills but weak soft skills",
                "decision": "Proceed to next round with a specific note on communication",
                "reasoning": "Technical depth is harder to find than communication training"
            }
        ],
        "confirmed_drop_zones": ["executive search"],
        "communication_style": {
            "tone": ["direct", "evaluative"],
            "verbosity": "concise",
            "preferred_framing": "Evidence-first"
        }
    })


def test_full_pipeline_end_to_end(
    mock_ingestion_response,
    mock_journalist_questions_response,
    mock_journalist_answers_response
):
    # 1. Setup mocks
    adapter = GenericAdapter()
    
    # Mock Ingestion LLM
    llm_ingestion = MagicMock()
    llm_ingestion.chat.return_value = mock_ingestion_response
    
    # Mock Journalist LLM (handles two turns)
    llm_journalist = MagicMock()
    responses = [mock_journalist_questions_response, mock_journalist_answers_response]
    llm_journalist.chat.side_effect = responses

    # 2. Build graph
    graph = build_extraction_graph(
        llm_ingestion=llm_ingestion,
        llm_journalist=llm_journalist,
        adapter=adapter
    )

    # 3. Create initial state with sample documents
    expert_id = str(uuid4())
    documents = [
        Document(
            source="case_1.txt",
            content="Technical depth is my priority. I've hired 50 engineers.",
            metadata={"type": "master_case"}
        ).to_dict()
    ]
    
    initial_state = create_initial_state(
        expert_id=expert_id,
        domain="generic",
        documents=documents,
        identity_override={"name": "Test Recruiter", "role": "Senior Talent Partner"}
    )

    # 4. Invoke the graph
    final_state = graph.invoke(initial_state)

    # 5. Assertions
    assert final_state["error"] is None
    assert final_state["final_manifest"] is not None
    
    manifest = json.loads(final_state["final_manifest"])
    assert manifest["identity"]["name"] == "Test Recruiter"
    assert manifest["identity"]["domain"] == "generic"
    assert len(manifest["heuristics"]) == 1
    assert "executive search" in manifest["drop_zone_triggers"]
    assert manifest["shadow_approved"] is False
