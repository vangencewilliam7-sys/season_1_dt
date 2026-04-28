"""
runtime/conversation/state.py

THE UNIVERSAL GRAPH STATE — Deliverable #1

This TypedDict is the single shared state object for the runtime
conversation graph. Every node reads from it and writes updates to it.

Fields:
    messages          — The full chat history (grows each turn)
    active_persona    — The loaded PersonaManifest JSON (set once at session start)
    retrieved_context — Populated by Harini's retrieval tool (RAG results)
    escalation_flag   — True if the query violated the persona's boundaries
    escalation_reason — Which drop zone or rule triggered the escalation
    route_decision    — The router's verdict: "respond" or "escalate"
    response          — The final response text to return to the user

Design Note:
    active_persona is a plain dict (not a Pydantic PersonaManifest) because
    LangGraph state values must be JSON-serializable. We validate with
    Pydantic at load time, then store the serialized dict for the graph.
"""

from typing import TypedDict, Optional


class ConversationState(TypedDict):
    """
    The shared state passed between all nodes in the conversation graph.

    LangGraph threading:
        Each node receives this state and returns a dict of updates.
        LangGraph merges the updates into the state and passes it
        to the next node. Nodes should never mutate state in place.
    """

    # ── Chat History ──────────────────────────────────────────────────────────
    # Grows with each conversation turn.
    # Format: [{"role": "user"|"assistant", "content": str}, ...]
    messages: list[dict]

    # ── Active Persona (the loaded PersonaManifest) ───────────────────────────
    # Set once when the conversation session starts. Never modified mid-session.
    # Contains: identity, communication_style, heuristics, drop_zone_triggers,
    #           confidence_threshold, fallback_identity (from adapter), etc.
    active_persona: dict

    # ── RAG Context (populated by Harini's retrieval tool) ────────────────────
    # The relevant expert knowledge retrieved from the vector DB.
    # Empty string if no retrieval has been performed yet.
    retrieved_context: str

    # ── Escalation (for Harshitha's system) ───────────────────────────────────
    # escalation_flag: True = the user's query is outside the persona's scope
    # escalation_reason: Human-readable explanation of why it was escalated
    escalation_flag: bool
    escalation_reason: str

    # ── Internal Routing ──────────────────────────────────────────────────────
    # route_decision: The router's verdict — "respond" or "escalate"
    # response: The final text response to return to the user
    route_decision: str
    response: str


def create_conversation_state(
    persona_dict: dict,
    user_message: str,
    domain_adapter_fallback: dict = None,
) -> ConversationState:
    """
    Factory function to create a fresh ConversationState for a new turn.

    Args:
        persona_dict: The full PersonaManifest as a dict (already validated).
        user_message: The user's incoming message text.
        domain_adapter_fallback: Optional fallback identity from the adapter.
                                 Merged into persona if not already present.

    Returns:
        A fully initialized ConversationState ready for graph.invoke().
    """
    # Merge fallback identity into persona if the adapter provides one
    persona = dict(persona_dict)  # shallow copy — don't mutate the original
    if domain_adapter_fallback and "fallback_identity" not in persona:
        persona["fallback_identity"] = domain_adapter_fallback

    return ConversationState(
        messages=[{"role": "user", "content": user_message}],
        active_persona=persona,
        retrieved_context="",
        escalation_flag=False,
        escalation_reason="",
        route_decision="",
        response="",
    )
