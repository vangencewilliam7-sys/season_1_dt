"""
core/nodes/compiler_node.py

STEP 3 — Manifest Compiler

Takes the journalist's validated findings and compiles them into
a fully structured, Pydantic-validated PersonaManifest.

If compilation fails validation, it logs what's missing — rather than
producing a silently incomplete Manifest.

Input:  ExtractionState with journalist_findings{} fully populated
Output: ExtractionState with final_manifest (serialized JSON string) populated

Rule: This node must never import from adapters/ or runtime/
"""

import json
import logging
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from core.schemas import (
    ExtractionState,
    PersonaManifest,
    Identity,
    CommunicationStyle,
    Heuristic,
)

if TYPE_CHECKING:
    from adapters.base_adapter import DomainAdapter

logger = logging.getLogger(__name__)


def compiler_node(
    state: ExtractionState,
    adapter: "DomainAdapter",
) -> ExtractionState:
    """
    Manifest Compiler node — assembles and validates the PersonaManifest.
    No LLM call here — purely structural assembly and Pydantic validation.
    """
    logger.info(f"[CompilerNode] Compiling manifest for expert: {state['expert_id']}")

    findings = state.get("processed_findings", {})
    documents = state.get("documents", [])

    if not findings:
        return {**state, "error": "CompilerNode: No processed findings available."}

    # ── Build Identity ────────────────────────────────────────────────────────
    # The identity fields come from the extraction context the adapter provides.
    # In a real system, expert name/role can be passed in the extraction request.
    identity_raw = state.get("identity_override", {})
    identity = Identity(
        name=identity_raw.get("name", "Unknown Expert"),
        role=identity_raw.get("role", "Unknown Role"),
        domain=adapter.get_domain_id(),
    )

    # ── Build Communication Style ─────────────────────────────────────────────
    style_raw = findings.get("communication_style", {})
    communication_style = CommunicationStyle(
        tone=style_raw.get("tone", ["professional"]),
        verbosity=style_raw.get("verbosity", "adaptive"),
        preferred_framing=style_raw.get("preferred_framing", "Not determined"),
    )

    # ── Build Heuristics ──────────────────────────────────────────────────────
    heuristics = []
    for h in findings.get("confirmed_heuristics", []):
        try:
            heuristics.append(Heuristic(
                trigger=h.get("trigger", ""),
                decision=h.get("decision", ""),
                reasoning=h.get("reasoning", ""),
            ))
        except Exception as e:
            logger.warning(f"[CompilerNode] Skipping malformed heuristic: {h} — {e}")

    # ── Build Drop Zones ──────────────────────────────────────────────────────
    drop_zones = findings.get("confirmed_drop_zones", [])

    # ── Source Document Provenance ────────────────────────────────────────────
    source_docs = [doc.get("source", "unknown") for doc in documents]

    # ── Validate minimum quality bar ─────────────────────────────────────────
    issues = []
    if len(heuristics) < 3:
        issues.append(f"Only {len(heuristics)} heuristics extracted (minimum 3 required)")
    if len(drop_zones) < 1:
        issues.append("No drop zones identified — expertise boundaries are undefined")
    if communication_style.preferred_framing == "Not determined":
        issues.append("Communication framing could not be determined from documents")

    if issues:
        logger.warning(f"[CompilerNode] Quality issues detected:\n" +
                       "\n".join(f"  - {i}" for i in issues))
        # We still compile — but flag these for Shadow Mode reviewer attention

    # ── Assemble the Manifest ─────────────────────────────────────────────────
    try:
        manifest = PersonaManifest(
            expert_id=UUID(state["expert_id"]) if _is_valid_uuid(state["expert_id"])
                      else __import__("uuid").uuid4(),
            extracted_at=datetime.now(__import__("datetime").UTC),
            manifest_version=1,
            source_documents=source_docs,
            identity=identity,
            communication_style=communication_style,
            heuristics=heuristics,
            drop_zone_triggers=drop_zones,
            confidence_threshold=0.70,  # Default; tuned during Shadow Mode
            shadow_approved=False,
        )

        manifest_json = manifest.model_dump_json(indent=2)

        logger.info(
            f"[CompilerNode] Manifest compiled successfully. "
            f"Heuristics: {len(heuristics)}, Drop zones: {len(drop_zones)}, "
            f"Quality issues: {len(issues)}"
        )

        return {
            **state,
            "final_manifest": manifest_json,
            "compilation_issues": issues,  # Passed to Shadow Mode reviewer
        }

    except Exception as e:
        logger.error(f"[CompilerNode] Manifest validation failed: {e}")
        return {**state, "error": f"CompilerNode validation error: {str(e)}"}


def _is_valid_uuid(val: str) -> bool:
    try:
        UUID(val)
        return True
    except ValueError:
        return False
