"""
runtime/conversation/graph.py

CONVERSATION GRAPH COMPILATION — Deliverable #3

Wires all conversation nodes into a LangGraph StateGraph with
dynamic conditional routing based on the active persona.

Flow:
    ingest_message → router → [retrieve_context → generate_response] OR [escalation] → END

Usage:
    graph = build_conversation_graph(llm=my_llm, adapter=my_adapter)
    state = create_conversation_state(persona_dict=manifest, user_message="Hello")
    result = graph.invoke(state)

This file must never import from core/nodes/ (that's the extraction pipeline).
"""

import logging
from functools import partial
from typing import TYPE_CHECKING

from langgraph.graph import StateGraph, END

from runtime.conversation.state import ConversationState, create_conversation_state
from runtime.conversation.nodes import (
    ingest_message_node,
    router_node,
    retrieve_context_node,
    generate_response_node,
    escalation_node,
)

if TYPE_CHECKING:
    from core.providers.base_llm import BaseLLMProvider
    from adapters.base_adapter import DomainAdapter

logger = logging.getLogger(__name__)


def _route_by_decision(state: ConversationState) -> str:
    """
    Conditional edge function — reads the router's verdict from state
    and routes to the appropriate branch.

    Returns:
        "respond"  → retrieve_context → generate_response
        "escalate" → escalation_node
    """
    decision = state.get("route_decision", "respond")
    logger.info(f"[Graph] Routing decision: {decision}")
    return decision


def build_conversation_graph(
    llm: "BaseLLMProvider" = None,
    adapter: "DomainAdapter" = None,
    embedding_service=None,
    vault_service=None,
):
    """
    Build and compile the conversation pipeline graph.

    Args:
        llm:               LLM provider for the router (intent classification)
                           and response generation. Can be None for keyword-only routing.
        adapter:           The domain adapter providing immutable rules and fallback identity.
                           Can be None for adapter-free operation.
        embedding_service: EmbeddingService for generating query vectors.
                           If None, retrieve_context_node falls back to heuristics.
        vault_service:     KnowledgeVaultService for searching the Logic Vault.
                           If None, retrieve_context_node falls back to heuristics.

    Returns:
        A compiled LangGraph graph ready to invoke with a ConversationState.

    Architecture:
        ┌─────────────────┐
        │  ingest_message  │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │   router_node    │  ← reads active_persona, checks drop zones
        └────────┬────────┘
                 │
            ┌────┴─────┐
            │          │
        "respond"  "escalate"
            │          │
       ┌────▼────┐  ┌──▼────────────┐
       │retrieve │  │ escalation     │
       │_context │  │ _node          │
       └────┬────┘  └──────┬────────┘
            │              │
       ┌────▼──────────┐   │
       │generate       │   │
       │_response      │   │
       └────┬──────────┘   │
            │              │
            └──────┬───────┘
                   │
                  END
    """
    # ── Bind dependencies into nodes via functools.partial ─────────────────
    # This keeps node functions pure — no global state, no singletons.
    bound_router = partial(router_node, llm=llm, adapter=adapter)
    bound_retrieve = partial(
        retrieve_context_node,
        embedding_service=embedding_service,
        vault_service=vault_service,
    )
    bound_generate = partial(generate_response_node, llm=llm, adapter=adapter)
    bound_escalation = partial(escalation_node, adapter=adapter)

    # ── Build the state graph ──────────────────────────────────────────────
    graph = StateGraph(ConversationState)

    # Register all nodes
    graph.add_node("ingest_message", ingest_message_node)
    graph.add_node("router", bound_router)
    graph.add_node("retrieve_context", bound_retrieve)
    graph.add_node("generate_response", bound_generate)
    graph.add_node("escalation", bound_escalation)

    # ── Wire the edges ─────────────────────────────────────────────────────

    # Entry point
    graph.set_entry_point("ingest_message")

    # ingest_message always goes to router
    graph.add_edge("ingest_message", "router")

    # Router → conditional split based on route_decision
    graph.add_conditional_edges(
        "router",
        _route_by_decision,
        {
            "respond": "retrieve_context",
            "escalate": "escalation",
        },
    )

    # retrieve_context → generate_response
    graph.add_edge("retrieve_context", "generate_response")

    # Both terminal nodes go to END
    graph.add_edge("generate_response", END)
    graph.add_edge("escalation", END)

    logger.info("[Graph] Conversation pipeline compiled: "
                "ingest → router → [retrieve+respond | escalate] → END")

    return graph.compile()

