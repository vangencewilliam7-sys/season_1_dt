"""
core/graph.py

LangGraph state machine — wires the 3 extraction nodes into a pipeline.

Flow:  ingestion_node → journalist_node → compiler_node → END

Each node is a pure function that receives ExtractionState and returns
an updated ExtractionState. The graph handles state threading automatically.

Rule: This file must never import from runtime/
"""

import logging
from functools import partial
from typing import TYPE_CHECKING

from langgraph.graph import StateGraph, END

from core.schemas import ExtractionState
from core.nodes.ingestion_node import ingestion_node
from core.nodes.journalist_node import journalist_node
from core.nodes.answer_processor_node import answer_processor_node
from core.nodes.compiler_node import compiler_node
from core.renderer import renderer_node
from langgraph.checkpoint.memory import MemorySaver

if TYPE_CHECKING:
    from core.providers.base_llm import BaseLLMProvider
    from adapters.base_adapter import DomainAdapter

logger = logging.getLogger(__name__)


def _should_continue(state: ExtractionState) -> str:
    """
    Conditional edge: if any node sets an error, route to END immediately.
    This prevents cascading failures through the pipeline.
    """
    if state.get("error"):
        logger.error(f"[Graph] Pipeline halted due to error: {state['error']}")
        return "end_with_error"
    return "continue"


def build_extraction_graph(
    llm_ingestion: "BaseLLMProvider",
    llm_journalist: "BaseLLMProvider",
    adapter: "DomainAdapter",
):
    """
    Build and compile the extraction pipeline graph.

    Args:
        llm_ingestion: LLM for the deep scan step (larger/more capable model)
        llm_journalist: LLM for the interview step (smaller/faster model)
        adapter: The domain adapter providing context and rules

    Returns:
        A compiled LangGraph graph ready to invoke with an ExtractionState.
    """
    # Bind dependencies into each node via partial application
    # This keeps node functions pure (no global state)
    bound_ingestion = partial(ingestion_node, llm=llm_ingestion, adapter=adapter)
    bound_journalist = partial(journalist_node, llm=llm_journalist, adapter=adapter)
    bound_answer_processor = partial(answer_processor_node, llm=llm_journalist, adapter=adapter)
    bound_compiler = partial(compiler_node, adapter=adapter)
    bound_renderer = partial(renderer_node, adapter=adapter)

    # ── Build the graph ───────────────────────────────────────────────────────
    graph = StateGraph(ExtractionState)

    graph.add_node("ingestion", bound_ingestion)
    graph.add_node("journalist", bound_journalist)
    graph.add_node("answer_processor", bound_answer_processor)
    graph.add_node("compiler", bound_compiler)
    graph.add_node("renderer", bound_renderer)

    # Entry point
    graph.set_entry_point("ingestion")

    # After ingestion: check for errors, then continue to journalist
    graph.add_conditional_edges(
        "ingestion",
        _should_continue,
        {
            "continue": "journalist",
            "end_with_error": END,
        },
    )

    # After journalist: check for errors, then continue to answer_processor
    graph.add_conditional_edges(
        "journalist",
        _should_continue,
        {
            "continue": "answer_processor",
            "end_with_error": END,
        },
    )

    # After answer_processor: check for errors, then continue to compiler
    graph.add_conditional_edges(
        "answer_processor",
        _should_continue,
        {
            "continue": "compiler",
            "end_with_error": END,
        },
    )

    # After compiler: check for errors, then continue to renderer
    graph.add_conditional_edges(
        "compiler",
        _should_continue,
        {
            "continue": "renderer",
            "end_with_error": END,
        },
    )

    # After renderer: always end (success or error)
    graph.add_edge("renderer", END)

    logger.info("[Graph] Extraction pipeline compiled: "
                "ingestion → journalist → [PAUSE] → answer_processor → compiler → renderer")

    memory = MemorySaver()
    return graph.compile(checkpointer=memory, interrupt_before=["answer_processor"])


def create_initial_state(
    expert_id: str,
    domain: str,
    documents: list,
    identity_override: dict = None,
) -> ExtractionState:
    """
    Create a fresh ExtractionState to start an extraction run.

    Args:
        expert_id: UUID string identifying the expert
        domain: Domain slug (from the active adapter)
        documents: List of serialized Document dicts from the reader
        identity_override: Optional {"name": str, "role": str} for the expert
    """
    return ExtractionState(
        expert_id=expert_id,
        domain=domain,
        documents=documents,
        behavioral_hypotheses=[],
        generated_questions=[],
        expert_answers=[],
        processed_findings={},
        final_manifest=None,
        final_prompt=None,
        error=None,
        identity_override=identity_override or {},
    )
