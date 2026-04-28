"""
runtime/conversation/nodes.py

All node functions for the runtime conversation graph.

Nodes:
    1. ingest_message_node   — Appends user message to chat history
    2. router_node           — THE DYNAMIC ROUTER (Deliverable #2)
                               Reads active_persona JSON → checks drop zones → routes
    3. retrieve_context_node — STUB for Harini's retrieval tool
    4. generate_response_node — Assembles persona-aware prompt → calls LLM → returns response
    5. escalation_node       — Sets escalation_flag, generates fallback response

Each node is a pure function:
    Input:  ConversationState (the shared state)
    Output: dict of state updates (LangGraph merges these)
"""

import json
import logging
from typing import TYPE_CHECKING

from runtime.conversation.state import ConversationState

if TYPE_CHECKING:
    from core.providers.base_llm import BaseLLMProvider
    from adapters.base_adapter import DomainAdapter

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# NODE 1: INGEST MESSAGE
# ══════════════════════════════════════════════════════════════════════════════

def ingest_message_node(state: ConversationState) -> dict:
    """
    Pure bookkeeping — ensures the user message is in the messages list.
    In a multi-turn scenario, this would append new messages.
    For single-turn invocation, the message is already set by create_conversation_state().
    """
    logger.info("[IngestMessage] Message received. Chat history length: "
                f"{len(state['messages'])}")
    # No-op for single-turn; in multi-turn you'd append here
    return {}


# ══════════════════════════════════════════════════════════════════════════════
# NODE 2: DYNAMIC ROUTER — THE CORE DELIVERABLE
# ══════════════════════════════════════════════════════════════════════════════

ROUTER_SYSTEM_PROMPT = """You are an intent classifier for a Digital Twin system.

You must decide if the user's query is within the expert's domain of knowledge.

THE EXPERT'S PERSONA:
- Name: {expert_name}
- Role: {expert_role}
- Domain: {expert_domain}

THE EXPERT DOES NOT HANDLE THESE TOPICS (Drop Zones):
{drop_zones}

THE USER'S QUERY:
"{user_message}"

INSTRUCTIONS:
1. If the query is about ANY topic in the Drop Zones list, respond with: {{"decision": "escalate", "reason": "Query matches drop zone: <which one>"}}
2. If the query is clearly outside the expert's domain (e.g., asking a recruiter about medical diagnosis), respond with: {{"decision": "escalate", "reason": "Query is outside expert's domain: <expert_domain>"}}
3. If the query is within the expert's domain and not in any drop zone, respond with: {{"decision": "respond", "reason": "Query is within scope"}}

Respond with ONLY valid JSON. No explanation."""


def router_node(
    state: ConversationState,
    llm: "BaseLLMProvider" = None,
    adapter: "DomainAdapter" = None,
) -> dict:
    """
    THE DYNAMIC ROUTER — Deliverable #2.

    This is the "LLM-Resistant" hard part. The router parses a dynamic
    PersonaManifest JSON at every invocation and uses it to make routing
    decisions. It does NOT hardcode any domain logic.

    Approach (2-layer):
        Layer A — Fast keyword pre-filter against drop_zone_triggers.
                  If a drop zone keyword appears in the user's message,
                  escalate immediately. No LLM call needed.
        Layer B — LLM-based intent classification for ambiguous queries.
                  Only runs if the keyword filter doesn't catch it AND
                  an LLM provider is available.
    """
    logger.info("[Router] Evaluating user query against active persona...")

    # ── Read the persona from state ───────────────────────────────────────────
    persona = state["active_persona"]
    drop_zones = persona.get("drop_zone_triggers", [])
    identity = persona.get("identity", {})
    expert_name = identity.get("name", "Unknown Expert")
    expert_role = identity.get("role", "Unknown Role")
    expert_domain = identity.get("domain", "unknown")

    # ── Get the latest user message ───────────────────────────────────────────
    messages = state.get("messages", [])
    if not messages:
        logger.error("[Router] No messages in state.")
        return {
            "route_decision": "escalate",
            "escalation_flag": True,
            "escalation_reason": "No user message found in state.",
        }

    user_message = messages[-1].get("content", "")
    user_message_lower = user_message.lower()

    logger.info(f"[Router] Expert: {expert_name} ({expert_role})")
    logger.info(f"[Router] Domain: {expert_domain}")
    logger.info(f"[Router] Drop zones: {drop_zones}")
    logger.info(f"[Router] User query: {user_message[:100]}...")

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER A — Fast Keyword Pre-Filter
    # Check if any drop zone trigger appears in the user's message.
    # This is intentionally simple — catches obvious violations instantly.
    # ══════════════════════════════════════════════════════════════════════════

    for trigger in drop_zones:
        trigger_lower = trigger.lower()
        # Check if the drop zone phrase (or significant keywords from it)
        # appears in the user's message
        trigger_words = [w for w in trigger_lower.split() if len(w) > 3]

        # Match if the full trigger phrase or majority of its keywords appear
        if trigger_lower in user_message_lower:
            reason = f"Query matches drop zone: '{trigger}'"
            logger.info(f"[Router] KEYWORD MATCH — {reason}")
            return {
                "route_decision": "escalate",
                "escalation_flag": True,
                "escalation_reason": reason,
            }

        # Also check if most keywords from the trigger are present
        if trigger_words:
            matches = sum(1 for w in trigger_words if w in user_message_lower)
            if matches >= len(trigger_words) * 0.7:  # 70% keyword overlap
                reason = f"Query matches drop zone: '{trigger}'"
                logger.info(f"[Router] KEYWORD OVERLAP — {reason}")
                return {
                    "route_decision": "escalate",
                    "escalation_flag": True,
                    "escalation_reason": reason,
                }

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER B — LLM-Based Intent Classification (for ambiguous queries)
    # Only runs if an LLM provider is available.
    # ══════════════════════════════════════════════════════════════════════════

    if llm is not None:
        try:
            drop_zones_text = "\n".join(f"- {dz}" for dz in drop_zones)
            prompt = ROUTER_SYSTEM_PROMPT.format(
                expert_name=expert_name,
                expert_role=expert_role,
                expert_domain=expert_domain,
                drop_zones=drop_zones_text,
                user_message=user_message,
            )

            response = llm.chat(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Classify this query."},
                ],
                temperature=0.1,   # Very low — deterministic classification
                max_tokens=200,
            )

            result = json.loads(response)
            decision = result.get("decision", "respond")
            reason = result.get("reason", "LLM classification")

            logger.info(f"[Router] LLM DECISION — {decision}: {reason}")

            return {
                "route_decision": decision,
                "escalation_flag": decision == "escalate",
                "escalation_reason": reason if decision == "escalate" else "",
            }

        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"[Router] LLM classification failed: {e}. "
                           "Defaulting to 'respond'.")

    # ══════════════════════════════════════════════════════════════════════════
    # DEFAULT — No keyword match, no LLM flag → allow the query
    # ══════════════════════════════════════════════════════════════════════════

    logger.info("[Router] No drop zone violation detected. Routing to response.")
    return {
        "route_decision": "respond",
        "escalation_flag": False,
        "escalation_reason": "",
    }


# ══════════════════════════════════════════════════════════════════════════════
# NODE 3: RETRIEVE CONTEXT — STUB FOR HARINI
# ══════════════════════════════════════════════════════════════════════════════

def retrieve_context_node(
    state: ConversationState,
    embedding_service=None,
    vault_service=None,
) -> dict:
    """
    KNOWLEDGE HUB RETRIEVAL — replaces the original stub.

    Integration contract (unchanged):
        INPUT:  state["messages"], state["active_persona"]
        OUTPUT: {"retrieved_context": "relevant expert knowledge from vector DB"}

    Data flow:
        1. Embed the user's query using the same model as the Knowledge Hub
        2. Search the expert_dna table (high-purity verified decisions)
        3. Search document_chunks as supplementary context
        4. Fallback to persona heuristics if Knowledge Hub is unavailable

    The graph never changes — only this function body was replaced.
    """
    persona = state["active_persona"]
    identity = persona.get("identity", {})
    expert_domain = identity.get("domain", "")
    heuristics = persona.get("heuristics", [])

    # ── Get the user's latest message ─────────────────────────────────────
    messages = state.get("messages", [])
    if not messages:
        return {"retrieved_context": "No user message to retrieve context for."}

    user_message = messages[-1].get("content", "")
    logger.info(f"[RetrieveContext] Query: {user_message[:100]}...")

    # ══════════════════════════════════════════════════════════════════════
    # PRIMARY: Knowledge Hub vector search (if services are available)
    # ══════════════════════════════════════════════════════════════════════

    if embedding_service is not None and vault_service is not None and vault_service.is_connected:
        try:
            # 1. Generate query embedding
            query_vector = embedding_service.get_embedding(user_message)

            context_sections = []

            # 2. Search expert_dna (high-purity verified decisions)
            dna_results = vault_service.search_expert_dna(
                query_embedding=query_vector,
                threshold=0.65,  # Slightly lower than KH's default to catch more
                limit=3,
            )

            # Filter by domain/industry if the expert has a specific domain
            if expert_domain and dna_results:
                domain_filtered = [
                    r for r in dna_results
                    if r.get("industry", "").lower() == expert_domain.lower()
                ]
                # Use domain-filtered results if we have any, otherwise use all
                if domain_filtered:
                    dna_results = domain_filtered

            if dna_results:
                context_sections.append(
                    "═══ VERIFIED EXPERT DECISIONS (from Logic Vault) ═══"
                )
                for i, result in enumerate(dna_results, 1):
                    similarity = result.get("similarity", 0)
                    context_sections.append(
                        f"\n[Decision {i}] (confidence: {similarity:.2f})\n"
                        f"  Expert Decision: {result.get('expert_decision', 'N/A')}\n"
                        f"  Reasoning: {result.get('reasoning', 'N/A')}\n"
                        f"  Impact Level: {result.get('impact_archetype', 'N/A')}\n"
                        f"  Domain: {result.get('industry', 'N/A')}"
                    )
                logger.info(f"[RetrieveContext] Found {len(dna_results)} verified "
                            f"decisions from Logic Vault.")

            # 3. Search raw document_chunks (supplementary, unverified)
            chunk_results = vault_service.search_raw_chunks(
                query_embedding=query_vector,
                threshold=0.60,
                limit=3,
            )

            if chunk_results:
                context_sections.append(
                    "\n═══ SUPPLEMENTARY KNOWLEDGE (from Knowledge Hub) ═══"
                )
                for i, chunk in enumerate(chunk_results, 1):
                    similarity = chunk.get("similarity", 0)
                    context_sections.append(
                        f"\n[Source {i}] (relevance: {similarity:.2f})\n"
                        f"  Content: {chunk.get('content', 'N/A')[:500]}\n"
                        f"  Source: {chunk.get('source_path', 'N/A')}"
                    )
                logger.info(f"[RetrieveContext] Found {len(chunk_results)} "
                            f"supplementary chunks.")

            if context_sections:
                return {"retrieved_context": "\n".join(context_sections)}

            logger.info("[RetrieveContext] No Knowledge Hub results found. "
                        "Falling back to persona heuristics.")

        except Exception as e:
            logger.error(f"[RetrieveContext] Knowledge Hub search failed: {e}. "
                         "Falling back to persona heuristics.")

    else:
        logger.info("[RetrieveContext] Knowledge Hub services not available. "
                    "Using persona heuristics as context.")

    # ══════════════════════════════════════════════════════════════════════
    # FALLBACK: Use persona heuristics as context
    # (Original stub behavior — ensures the system always works)
    # ══════════════════════════════════════════════════════════════════════

    context_parts = []
    for h in heuristics:
        context_parts.append(
            f"- When: {h.get('trigger', '')}\n"
            f"  Do: {h.get('decision', '')}\n"
            f"  Why: {h.get('reasoning', '')}"
        )

    fallback_context = (
        "RETRIEVED CONTEXT (from expert's persona heuristics):\n"
        + "\n".join(context_parts) if context_parts
        else "No relevant context found in knowledge base."
    )

    return {"retrieved_context": fallback_context}


# ══════════════════════════════════════════════════════════════════════════════
# NODE 4: GENERATE RESPONSE
# ══════════════════════════════════════════════════════════════════════════════

RESPONSE_SYSTEM_PROMPT = """You are {expert_name}, a {expert_role}.

{domain_rules}

[YOUR PERSONA]
Communication Style:
- Tone: {tone}
- Verbosity: {verbosity}
- Framing: {framing}

[YOUR DECISION HEURISTICS]
{heuristics_text}

[RELEVANT CONTEXT FROM YOUR KNOWLEDGE BASE]
{retrieved_context}

[INSTRUCTIONS]
Respond to the user's question AS {expert_name}. Use your heuristics and the
retrieved context to ground your answer. Stay in character. If the question
is slightly outside your expertise but still adjacent, answer cautiously and
flag your uncertainty. Never fabricate information."""


def generate_response_node(
    state: ConversationState,
    llm: "BaseLLMProvider" = None,
    adapter: "DomainAdapter" = None,
) -> dict:
    """
    Assembles the 3-layer prompt and generates a persona-aware response.

    Prompt assembly order (architecturally significant):
        1. Domain safety rules (from adapter) — ALWAYS FIRST, cannot be overridden
        2. Persona identity + heuristics (from active_persona)
        3. Retrieved context (from Harini's tool)
    """
    logger.info("[GenerateResponse] Assembling persona-aware response...")

    persona = state["active_persona"]
    identity = persona.get("identity", {})
    style = persona.get("communication_style", {})
    heuristics = persona.get("heuristics", [])
    retrieved_context = state.get("retrieved_context", "")

    # Build heuristics text
    heuristics_text = ""
    for i, h in enumerate(heuristics, 1):
        heuristics_text += (
            f"{i}. WHEN: {h.get('trigger', '')}\n"
            f"   DO: {h.get('decision', '')}\n"
            f"   WHY: {h.get('reasoning', '')}\n\n"
        )

    # Get domain rules from adapter (Layer 2 injection)
    domain_rules = ""
    if adapter is not None:
        domain_rules = adapter.get_immutable_rules()

    system_prompt = RESPONSE_SYSTEM_PROMPT.format(
        expert_name=identity.get("name", "Expert"),
        expert_role=identity.get("role", "Specialist"),
        domain_rules=domain_rules,
        tone=", ".join(style.get("tone", ["professional"])),
        verbosity=style.get("verbosity", "adaptive"),
        framing=style.get("preferred_framing", "Direct"),
        heuristics_text=heuristics_text or "No specific heuristics loaded.",
        retrieved_context=retrieved_context or "No additional context available.",
    )

    # Build message history for the LLM
    llm_messages = [{"role": "system", "content": system_prompt}]
    for msg in state.get("messages", []):
        llm_messages.append({"role": msg["role"], "content": msg["content"]})

    # If no LLM is available, return a placeholder
    if llm is None:
        logger.warning("[GenerateResponse] No LLM provider. Returning stub response.")
        response_text = (
            f"[STUB RESPONSE as {identity.get('name', 'Expert')}] "
            f"I would answer this based on my heuristics and retrieved context. "
            f"LLM provider not available for actual generation."
        )
    else:
        try:
            response_text = llm.chat(
                messages=llm_messages,
                temperature=0.4,
                max_tokens=1024,
            )
            logger.info(f"[GenerateResponse] Generated {len(response_text)} char response.")
        except Exception as e:
            logger.error(f"[GenerateResponse] LLM call failed: {e}")
            response_text = (
                f"I apologize, but I'm experiencing a technical issue. "
                f"As {identity.get('name', 'your expert')}, I'd normally "
                f"provide a detailed answer based on my experience. "
                f"Please try again."
            )

    # Append the response to messages for conversation history
    updated_messages = list(state.get("messages", []))
    updated_messages.append({"role": "assistant", "content": response_text})

    return {
        "messages": updated_messages,
        "response": response_text,
    }


# ══════════════════════════════════════════════════════════════════════════════
# NODE 5: ESCALATION
# ══════════════════════════════════════════════════════════════════════════════

def escalation_node(
    state: ConversationState,
    adapter: "DomainAdapter" = None,
) -> dict:
    """
    Handles out-of-scope queries gracefully.

    Reads the fallback identity from the persona (originally set by the adapter)
    and generates a polite deflection that explains WHY the expert can't help
    and WHAT the user should do instead.

    Sets escalation_flag = True so Harshitha's system can pick it up downstream.
    """
    logger.info("[Escalation] Query is outside persona scope. Generating fallback.")

    persona = state["active_persona"]
    identity = persona.get("identity", {})
    expert_name = identity.get("name", "Expert")
    escalation_reason = state.get("escalation_reason", "Topic is outside expertise")

    # Get fallback identity — either from the persona dict or from the adapter
    fallback = persona.get("fallback_identity", {})
    if not fallback and adapter is not None:
        fallback = adapter.get_fallback_identity()

    fallback_role = fallback.get("role", "Support Agent")
    fallback_tone = fallback.get("tone", "helpful")
    fallback_action = fallback.get("action", "Suggest consulting a specialist")

    # Generate the escalation response
    response_text = (
        f"I appreciate the question, but this falls outside my area of expertise. "
        f"{escalation_reason}. "
        f"As {expert_name}, I focus specifically on {identity.get('domain', 'my domain')}. "
        f"I'd recommend reaching out to a {fallback_role} who can help you with this. "
        f"{fallback_action}."
    )

    # Append to messages
    updated_messages = list(state.get("messages", []))
    updated_messages.append({"role": "assistant", "content": response_text})

    logger.info(f"[Escalation] Reason: {escalation_reason}")
    logger.info(f"[Escalation] Fallback: {fallback_role}")

    return {
        "messages": updated_messages,
        "response": response_text,
        "escalation_flag": True,
    }
