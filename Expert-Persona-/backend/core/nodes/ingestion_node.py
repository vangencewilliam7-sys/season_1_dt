"""
core/nodes/ingestion_node.py

STEP 1 — Deep Scan (Passive Ingestion)

Reads all raw documents from the Knowledge Hub + Master Cases.
Semantically analyses them to extract behavioral hypotheses about the expert.

Input:  ExtractionState with documents[] populated
Output: ExtractionState with behavioral_hypotheses[] populated

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

INGESTION_SYSTEM_PROMPT = """You are an expert behavioral analyst performing a deep semantic scan of an expert's professional documents.

Your task is to extract SPECIFIC, EVIDENCE-BASED behavioral hypotheses about this expert's:
1. Decision-making patterns (what they decide, in what situations)
2. Risk tolerance and thresholds
3. Communication preferences
4. Knowledge boundaries (what they avoid or defer)
5. Reasoning style (data-driven vs intuitive, cautious vs bold)

Domain context for this expert:
{domain_context}

CRITICAL RULES:
- Be specific, not generic. "Tends to ask clarifying questions before committing" is good. "Is a good communicator" is useless.
- Ground every hypothesis in evidence from the documents ("In case X, they stated...")
- Flag uncertainty: if a pattern appears only once, note that.
- Identify potential knowledge gaps — topics the expert skirts or defers.

Output ONLY valid JSON in this exact format:
{{
    "hypotheses": [
        "Specific behavioral hypothesis grounded in document evidence",
        "Another specific hypothesis..."
    ],
    "observed_knowledge_gaps": [
        "Topic or area the expert appears to avoid or defer",
        ...
    ]
}}"""


def ingestion_node(
    state: ExtractionState,
    llm: "BaseLLMProvider",
    adapter: "DomainAdapter",
) -> ExtractionState:
    """
    Deep Scan node — reads documents, extracts behavioral hypotheses.
    Uses the larger/more capable LLM (e.g., Llama 3.1 70B).
    """
    logger.info(f"[IngestionNode] Starting deep scan for expert: {state['expert_id']}")

    documents = state.get("documents", [])
    if not documents:
        return {**state, "error": "No documents provided for ingestion."}

    # Combine all documents into a single analysable corpus
    corpus = "\n\n" + ("=" * 60) + "\n\n".join([
        f"DOCUMENT: {doc.get('source', 'unknown')}\n\n{doc.get('content', '')}"
        for doc in documents
    ])

    logger.info(f"[IngestionNode] Analysing {len(documents)} documents "
                f"({len(corpus)} characters)")

    system_prompt = INGESTION_SYSTEM_PROMPT.format(
        domain_context=adapter.get_extraction_context()
    )

    try:
        response = llm.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Documents to analyse:\n{corpus}"},
            ],
            temperature=0.2,   # Low temperature for analytical consistency
            max_tokens=4096,
        )

        # Parse JSON response
        data = json.loads(response)
        hypotheses = data.get("hypotheses", [])
        knowledge_gaps = data.get("observed_knowledge_gaps", [])

        logger.info(f"[IngestionNode] Extracted {len(hypotheses)} hypotheses, "
                    f"{len(knowledge_gaps)} knowledge gaps")

        return {
            **state,
            "behavioral_hypotheses": hypotheses,
            # Pre-populate drop zones from observed gaps (journalist will refine)
            "journalist_findings": {
                "preliminary_drop_zones": knowledge_gaps
            },
        }

    except json.JSONDecodeError as e:
        logger.error(f"[IngestionNode] Failed to parse LLM response as JSON: {e}")
        return {**state, "error": f"IngestionNode JSON parse error: {str(e)}"}

    except Exception as e:
        logger.error(f"[IngestionNode] Unexpected error: {e}")
        return {**state, "error": f"IngestionNode error: {str(e)}"}
