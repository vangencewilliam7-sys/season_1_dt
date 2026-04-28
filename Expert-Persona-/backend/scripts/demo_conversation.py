"""
scripts/demo_conversation.py

Interactive demo of the Conversation Graph.
Loads a PersonaManifest, sends test messages, and shows routing decisions.

Usage:
    python scripts/demo_conversation.py
"""

import sys
import os
import json
import logging

# Add project root to path
sys.path.append(os.getcwd())

from runtime.conversation.graph import build_conversation_graph
from runtime.conversation.state import create_conversation_state

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("ConversationDemo")


# ── The test persona (Alex Rivet) ─────────────────────────────────────────────

ALEX_RIVET_PERSONA = {
    "expert_id": "demo-alex-001",
    "identity": {
        "name": "Alex Rivet",
        "role": "Principal Solutions Architect",
        "domain": "tech_consulting",
    },
    "communication_style": {
        "tone": ["direct", "pragmatic", "skeptical of hype"],
        "verbosity": "concise",
        "preferred_framing": "Risk-first evaluation",
    },
    "heuristics": [
        {
            "trigger": "When a performance bottleneck exists in a legacy DB during a time-sensitive period",
            "decision": "Use Redis caching/buffering instead of a DB migration",
            "reasoning": "Stability is more important than the 'perfect' DB when deadlines are short",
        },
        {
            "trigger": "When presented with a legacy migration request",
            "decision": "Force decomposition of the monolith into serverless/modern components",
            "reasoning": "Migration is the ONLY time you have political leverage to fix architectural debt",
        },
    ],
    "drop_zone_triggers": [
        "Mobile UX design",
        "Legacy Mainframe COBOL",
        "Frontend performance tuning",
        "Mobile application design",
        "Frontend Frameworks",
    ],
    "confidence_threshold": 0.7,
    "fallback_identity": {
        "role": "Consulting Associate",
        "tone": "helpful, analytical",
        "action": "State that this needs a Principal Architect's review",
    },
}


# ── Test messages ──────────────────────────────────────────────────────────────

TEST_MESSAGES = [
    {
        "label": "IN-SCOPE: Database bottleneck",
        "message": "Our PostgreSQL database is hitting a bottleneck during peak hours. Should we migrate to NoSQL?",
        "expected_route": "respond",
    },
    {
        "label": "DROP ZONE HIT: Frontend Frameworks",
        "message": "How do I set up a React component with Frontend Frameworks for our dashboard?",
        "expected_route": "escalate",
    },
    {
        "label": "DROP ZONE HIT: Mobile UX design",
        "message": "Can you help me design the mobile UX design for our iOS app?",
        "expected_route": "escalate",
    },
]


def run_demo():
    print("\n" + "=" * 70)
    print("  CONVERSATION GRAPH DEMO")
    print("=" * 70)

    # Load persona
    persona = ALEX_RIVET_PERSONA
    identity = persona["identity"]

    print(f"\n  Loaded Persona: {identity['name']} ({identity['role']})")
    print(f"  Domain: {identity['domain']}")
    print(f"  Drop Zones: {persona['drop_zone_triggers']}")
    print(f"  Heuristics: {len(persona['heuristics'])} loaded")

    # Build graph (no LLM — keyword routing only)
    graph = build_conversation_graph(llm=None, adapter=None)

    print("\n" + "-" * 70)

    for i, test in enumerate(TEST_MESSAGES, 1):
        print(f"\n  --- Test {i}: {test['label']} ---")
        print(f"  User: \"{test['message']}\"")

        state = create_conversation_state(
            persona_dict=persona,
            user_message=test["message"],
        )

        result = graph.invoke(state)

        route = result["route_decision"]
        escalated = result["escalation_flag"]
        reason = result.get("escalation_reason", "")
        response = result.get("response", "")

        status = "[PASS]" if route == test["expected_route"] else "[FAIL] UNEXPECTED"

        print(f"  Route: {route.upper()} {status}")
        print(f"  Escalated: {escalated}")
        if reason:
            print(f"  Reason: {reason}")
        if response:
            print(f"  Response: {response[:150]}...")

    print("\n" + "=" * 70)
    print("  DEMO COMPLETE")
    print("=" * 70 + "\n")


# ── Also try loading a real manifest file if it exists ─────────────────────────

def run_from_file():
    """Load a real PersonaManifest from the output file and run queries against it."""
    manifest_path = "output_manifest_expert_archi_001.json"

    if not os.path.exists(manifest_path):
        print(f"\n  (No real manifest found at {manifest_path} — using hardcoded persona)")
        return

    print(f"\n  Loading real manifest from: {manifest_path}")
    with open(manifest_path, "r") as f:
        persona = json.load(f)

    # Add fallback identity if not present
    if "fallback_identity" not in persona:
        persona["fallback_identity"] = {
            "role": "General Support Agent",
            "tone": "neutral, helpful",
            "action": "Suggest consulting a specialist",
        }

    graph = build_conversation_graph(llm=None, adapter=None)

    # Test with a few queries
    queries = [
        "How should I handle a legacy migration to AWS?",
        "Help me optimize React rendering performance with Frontend Frameworks",
        "What's the best mobile UX design pattern for e-commerce?",
    ]

    identity = persona.get("identity", {})
    print(f"  Expert: {identity.get('name')} ({identity.get('role')})")
    print(f"  Drop Zones: {persona.get('drop_zone_triggers', [])}")

    for q in queries:
        state = create_conversation_state(persona_dict=persona, user_message=q)
        result = graph.invoke(state)
        flag = "ESCALATE" if result["escalation_flag"] else "RESPOND"
        print(f"\n  [{flag}] {q[:60]}...")
        if result["escalation_reason"]:
            print(f"           Reason: {result['escalation_reason']}")


if __name__ == "__main__":
    run_demo()
    run_from_file()
