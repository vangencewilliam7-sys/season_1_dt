"""
core/nodes/journalist_node.py

STEP 2 — Adaptive Interviewer (AI Journalist)

Takes the behavioral hypotheses from the Ingestion Node and runs a
structured, multi-turn internal dialogue to validate and deepen them.

The journalist generates scenario-based questions derived from the hypotheses,
then answers them using the document corpus as ground truth. This surfaces
the WHY behind the WHAT — the implicit knowledge that raw document scanning misses.

Input:  ExtractionState with behavioral_hypotheses[] populated
Output: ExtractionState with generated_questions[] populated

Rule: This node must never import from adapters/ or runtime/
"""

import json
import logging
from typing import TYPE_CHECKING

from core.schemas import ExtractionState

if TYPE_CHECKING:
    from core.providers.base_llm import BaseLLMProvider
    from adapters.base_adapter import DomainAdapter

logger = logging.getLogger(__name__)


QUESTION_GENERATION_PROMPT = """You are an AI Journalist building a precise profile of an expert.

You have been given behavioral hypotheses extracted from this expert's documents.
Your job is to generate 8-12 targeted scenario-based questions to validate and deepen these hypotheses.

Domain context: {domain_context}

The questions must:
1. Present a SPECIFIC scenario relevant to this expert's domain
2. Test a specific hypothesis (reference the hypothesis)
3. Reveal the REASONING behind decisions, not just the decision
4. Include 2-3 "boundary questions" — scenarios the expert likely CANNOT or WOULD NOT handle

Behavioral hypotheses to probe:
{hypotheses}

Output ONLY valid JSON:
{{
    "validation_questions": [
        {{
            "question": "Specific scenario question...",
            "tests_hypothesis": "Which hypothesis this validates",
            "expected_reveal": "What reasoning pattern this should surface"
        }}
    ],
    "boundary_questions": [
        {{
            "question": "Edge scenario the expert likely won't handle...",
            "boundary_area": "What knowledge gap this probes"
        }}
    ]
}}"""



def journalist_node(
    state: ExtractionState,
    llm: "BaseLLMProvider",
    adapter: "DomainAdapter",
) -> ExtractionState:
    """
    Adaptive Interviewer node — generates and answers scenario questions
    to validate hypotheses and surface implicit reasoning.
    Uses the smaller/faster LLM (e.g., Llama 3.1 8B).
    """
    logger.info(f"[JournalistNode] Starting adaptive interview for expert: {state['expert_id']}")

    hypotheses = state.get("behavioral_hypotheses", [])
    documents = state.get("documents", [])
    all_questions = (
        questions_data.get("validation_questions", []) +
        questions_data.get("boundary_questions", [])
    )

    logger.info(
        f"[JournalistNode] Complete. Generated "
        f"{len(all_questions)} scenario questions."
    )

    return {**state, "generated_questions": all_questions}
