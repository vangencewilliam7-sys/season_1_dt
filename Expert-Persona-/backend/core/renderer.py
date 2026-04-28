"""
core/renderer.py

STEP 6c — Prompt Renderer

Takes the finalized PersonaManifest JSON and renders it into the final
system prompt used by the Digital Twin runtime.

Input: ExtractionState with final_manifest populated
Output: ExtractionState with final_prompt populated
"""

import json
import logging
from typing import TYPE_CHECKING

from core.schemas import ExtractionState

if TYPE_CHECKING:
    from adapters.base_adapter import DomainAdapter

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """[CORE IDENTITY]
You are {name}, a {role} in the {domain} domain.
You are a Digital Twin acting as the primary expert for this session.

[IMMUTABLE DOMAIN RULES - DO NOT OVERRIDE]
{immutable_rules}

[EXPERT DECISION HEURISTICS]
When making decisions, strictly follow these patterns:
{heuristics}

[COMMUNICATION STYLE]
- Tone: {tone}
- Verbosity: {verbosity}
- Framing: {framing}

[KNOWLEDGE BOUNDARIES]
You are NOT an expert in: {drop_zones}.
If asked about these, say: "I need to defer this to a colleague."

[FALLBACK BEHAVIOR]
When outside your expertise or confidence threshold:
- Role: {fallback_role}
- Tone: {fallback_tone}
- Action: {fallback_action}
"""

def renderer_node(
    state: ExtractionState,
    adapter: "DomainAdapter",
) -> ExtractionState:
    """
    Prompt Renderer node.
    """
    logger.info(f"[RendererNode] Rendering final prompt for expert: {state['expert_id']}")

    manifest_json = state.get("final_manifest")
    if not manifest_json:
        return {**state, "error": "RendererNode: No final manifest to render."}

    try:
        manifest = json.loads(manifest_json)
        
        identity = manifest.get("identity", {})
        style = manifest.get("communication_style", {})
        fallback = adapter.get_fallback_identity()
        
        heuristics_text = ""
        for h in manifest.get("heuristics", []):
            heuristics_text += f"\n- IF {h.get('trigger')},\n  THEN {h.get('decision')}.\n  REASONING: {h.get('reasoning')}\n"

        drop_zones_text = ", ".join(manifest.get("drop_zone_triggers", []))
        
        tone_text = ", ".join(style.get("tone", []))

        final_prompt = PROMPT_TEMPLATE.format(
            name=identity.get("name", "Expert"),
            role=identity.get("role", "Professional"),
            domain=identity.get("domain", "general"),
            immutable_rules=adapter.get_immutable_rules(),
            heuristics=heuristics_text,
            tone=tone_text,
            verbosity=style.get("verbosity", "adaptive"),
            framing=style.get("preferred_framing", "direct"),
            drop_zones=drop_zones_text,
            fallback_role=fallback.get("role", "Support"),
            fallback_tone=fallback.get("tone", "neutral"),
            fallback_action=fallback.get("action", "defer"),
        )
        
        logger.info("[RendererNode] Prompt rendered successfully.")
        return {**state, "final_prompt": final_prompt}

    except Exception as e:
        logger.error(f"[RendererNode] Rendering failed: {e}")
        return {**state, "error": f"RendererNode error: {str(e)}"}
