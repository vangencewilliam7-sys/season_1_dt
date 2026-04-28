"""
core/nodes/answer_processor_node.py

STEP 6a — Answer Processor

Takes the manual answers provided by the expert and extracts structured patterns
(heuristics, communication style, drop zones).

Input:  ExtractionState with expert_answers[] populated
Output: ExtractionState with processed_findings{} populated
"""

import json
import logging
from typing import TYPE_CHECKING

from core.schemas import ExtractionState

if TYPE_CHECKING:
    from core.providers.base_llm import BaseLLMProvider
    from adapters.base_adapter import DomainAdapter

logger = logging.getLogger(__name__)

PROCESS_ANSWERS_PROMPT = """You are analyzing an expert's manual answers to scenario questions.

Your job is to extract structured behavioral patterns from these answers.
Do not invent anything; only extract what is evident in the provided answers.

Domain rules for this expert:
{domain_rules}

Expert's Answers:
{answers}

Output ONLY valid JSON:
{{
    "confirmed_heuristics": [
        {{
            "trigger": "When situation X occurs...",
            "decision": "The expert typically does Y...",
            "reasoning": "Because of Z"
        }}
    ],
    "confirmed_drop_zones": [
        "Specific topic/scenario the expert deferred or stated was outside their scope"
    ],
    "communication_style": {{
        "tone": ["list", "of", "tone", "descriptors"],
        "verbosity": "concise | detailed | adaptive",
        "preferred_framing": "How the expert typically frames their responses"
    }}
}}"""


def answer_processor_node(
    state: ExtractionState,
    llm: "BaseLLMProvider",
    adapter: "DomainAdapter",
) -> ExtractionState:
    """
    Reads expert_answers and structures them into findings.
    """
    logger.info(f"[AnswerProcessorNode] Processing answers for expert: {state['expert_id']}")

    answers = state.get("expert_answers", [])
    if not answers:
        return {**state, "error": "AnswerProcessorNode: No expert answers provided."}

    answers_text = json.dumps(answers, indent=2)

    try:
        response = llm.chat(
            messages=[
                {
                    "role": "system",
                    "content": PROCESS_ANSWERS_PROMPT.format(
                        domain_rules=adapter.get_immutable_rules(),
                        answers=answers_text,
                    ),
                },
                {"role": "user", "content": "Extract heuristics and style from these answers."},
            ],
            temperature=0.3,
            max_tokens=2000,
        )
        findings = json.loads(response)

    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"[AnswerProcessorNode] Answer processing failed: {e}")
        return {**state, "error": f"AnswerProcessorNode processing error: {str(e)}"}

    logger.info(
        f"[AnswerProcessorNode] Complete. "
        f"Heuristics: {len(findings.get('confirmed_heuristics', []))}, "
        f"Drop zones: {len(findings.get('confirmed_drop_zones', []))}"
    )

    return {**state, "processed_findings": findings}
