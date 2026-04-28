"""
tests/test_conversation_graph.py

End-of-day deliverable tests for the Conversation Graph.

These tests prove:
1. In-scope queries route to generate_response (escalation_flag=False)
2. Drop zone violations route to escalation (escalation_flag=True)
3. Cross-domain violations are caught
4. Escalation reason is populated with the matching trigger
5. Different personas produce different routing for the same query

All tests use keyword-only routing (no LLM) — fully offline, zero API calls.
"""

import json
import pytest

from runtime.conversation.state import ConversationState, create_conversation_state
from runtime.conversation.graph import build_conversation_graph
from runtime.conversation.nodes import router_node


# ── Test Personas ──────────────────────────────────────────────────────────────

ALEX_RIVET_PERSONA = {
    "expert_id": "test-alex-001",
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

HR_RECRUITER_PERSONA = {
    "expert_id": "test-hr-001",
    "identity": {
        "name": "Sarah Chen",
        "role": "Senior Technical Recruiter",
        "domain": "recruiting",
    },
    "communication_style": {
        "tone": ["empathetic", "structured", "professional"],
        "verbosity": "detailed",
        "preferred_framing": "Evidence-first evaluation",
    },
    "heuristics": [
        {
            "trigger": "When a candidate has strong technical skills but poor communication",
            "decision": "Proceed to next round with a specific note on communication",
            "reasoning": "Technical depth is harder to find than communication training",
        },
    ],
    "drop_zone_triggers": [
        "Medical diagnosis",
        "Legal compliance advice",
        "Financial investment",
        "System architecture",
    ],
    "confidence_threshold": 0.8,
    "fallback_identity": {
        "role": "Recruiting Coordinator",
        "tone": "neutral, process-oriented",
        "action": "Acknowledge the gap and route to the senior recruiter",
    },
}


# ── Test 1: In-scope query routes to response ─────────────────────────────────

class TestInScopeRouting:

    def test_in_scope_query_routes_to_response(self):
        """
        'How should I handle database scaling?' is within Alex Rivet's domain.
        Should route to generate_response, escalation_flag = False.
        """
        graph = build_conversation_graph(llm=None, adapter=None)

        state = create_conversation_state(
            persona_dict=ALEX_RIVET_PERSONA,
            user_message="How should I handle a database scaling bottleneck?",
        )

        result = graph.invoke(state)

        assert result["escalation_flag"] is False
        assert result["route_decision"] == "respond"
        assert result["response"] != ""
        assert len(result["messages"]) >= 2  # user + assistant

    def test_recruiting_query_on_recruiter_persona(self):
        """
        'How do you evaluate a candidate with poor communication?' is within
        Sarah Chen's domain. Should respond, not escalate.
        """
        graph = build_conversation_graph(llm=None, adapter=None)

        state = create_conversation_state(
            persona_dict=HR_RECRUITER_PERSONA,
            user_message="How do you evaluate a candidate with strong Python skills but poor communication?",
        )

        result = graph.invoke(state)

        assert result["escalation_flag"] is False
        assert result["route_decision"] == "respond"


# ── Test 2: Drop zone violation escalates ──────────────────────────────────────

class TestDropZoneEscalation:

    def test_frontend_query_escalates_for_architect(self):
        """
        'How do I optimize React rendering?' hits Alex Rivet's drop zone
        'Frontend Frameworks'. Should escalate.
        """
        graph = build_conversation_graph(llm=None, adapter=None)

        state = create_conversation_state(
            persona_dict=ALEX_RIVET_PERSONA,
            user_message="How do I optimize React component rendering with Frontend Frameworks?",
        )

        result = graph.invoke(state)

        assert result["escalation_flag"] is True
        assert result["route_decision"] == "escalate"
        assert "Frontend Frameworks" in result["escalation_reason"]

    def test_mobile_query_escalates_for_architect(self):
        """
        'How should I design a mobile UX design flow?' hits 'Mobile UX design' drop zone.
        """
        graph = build_conversation_graph(llm=None, adapter=None)

        state = create_conversation_state(
            persona_dict=ALEX_RIVET_PERSONA,
            user_message="Can you help me with mobile UX design for our app?",
        )

        result = graph.invoke(state)

        assert result["escalation_flag"] is True
        assert result["route_decision"] == "escalate"


# ── Test 3: Cross-domain violation escalates ───────────────────────────────────

class TestCrossDomainEscalation:

    def test_medical_query_on_hr_persona_escalates(self):
        """
        'What medication should I prescribe for chest pain?' is a medical question
        asked to an HR Recruiter. Should hit 'Medical diagnosis' drop zone.
        """
        graph = build_conversation_graph(llm=None, adapter=None)

        state = create_conversation_state(
            persona_dict=HR_RECRUITER_PERSONA,
            user_message="What is the correct medical diagnosis for recurring chest pain?",
        )

        result = graph.invoke(state)

        assert result["escalation_flag"] is True
        assert result["route_decision"] == "escalate"

    def test_architecture_query_on_hr_persona_escalates(self):
        """
        'How should I design system architecture?' hits HR's 'System architecture' drop zone.
        """
        graph = build_conversation_graph(llm=None, adapter=None)

        state = create_conversation_state(
            persona_dict=HR_RECRUITER_PERSONA,
            user_message="We need help with system architecture for our new platform.",
        )

        result = graph.invoke(state)

        assert result["escalation_flag"] is True
        assert result["route_decision"] == "escalate"


# ── Test 4: Escalation reason is populated ─────────────────────────────────────

class TestEscalationReason:

    def test_escalation_reason_contains_trigger(self):
        """
        When escalated, escalation_reason must contain which drop zone matched.
        """
        graph = build_conversation_graph(llm=None, adapter=None)

        state = create_conversation_state(
            persona_dict=ALEX_RIVET_PERSONA,
            user_message="How do I tune frontend performance tuning for a dashboard?",
        )

        result = graph.invoke(state)

        assert result["escalation_flag"] is True
        assert "drop zone" in result["escalation_reason"].lower()
        assert any(
            trigger in result["escalation_reason"]
            for trigger in ALEX_RIVET_PERSONA["drop_zone_triggers"]
        )


# ── Test 5: Different persona = different routing ──────────────────────────────

class TestDynamicPersonaSwitching:

    def test_same_query_different_persona_different_routing(self):
        """
        The query 'How should I design system architecture?' should:
        - RESPOND for Alex Rivet (architecture IS his domain)
        - ESCALATE for Sarah Chen (architecture is her drop zone)

        This proves the graph is truly dynamic — not hardcoded.
        """
        graph = build_conversation_graph(llm=None, adapter=None)
        query = "How should I design system architecture for a new platform?"

        # Alex Rivet — architect — should respond
        alex_state = create_conversation_state(
            persona_dict=ALEX_RIVET_PERSONA,
            user_message=query,
        )
        alex_result = graph.invoke(alex_state)

        # Sarah Chen — recruiter — should escalate (architecture is her drop zone)
        sarah_state = create_conversation_state(
            persona_dict=HR_RECRUITER_PERSONA,
            user_message=query,
        )
        sarah_result = graph.invoke(sarah_state)

        # SAME query, DIFFERENT results — proves dynamic routing
        assert alex_result["escalation_flag"] is False, \
            "Alex Rivet should respond to architecture queries"
        assert sarah_result["escalation_flag"] is True, \
            "Sarah Chen should escalate architecture queries"
        assert alex_result["route_decision"] == "respond"
        assert sarah_result["route_decision"] == "escalate"
