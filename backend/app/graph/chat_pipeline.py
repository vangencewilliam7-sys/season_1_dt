from langgraph.graph import StateGraph, END
from ..models.chat_state import ChatState
from .nodes.chat_nodes import (
    retrieve_context_node, 
    reasoning_node, 
    validation_node,
    generation_node, 
    emergency_escalation_node,
    proxy_gathering_node,
    audit_node, 
    persistence_node
)
from .nodes.intent_detector import intent_detection_node
from .nodes.skill_executor import skill_executor_node

def create_chat_pipeline():
    workflow = StateGraph(ChatState)

    # Add Nodes
    workflow.add_node("intent_detection", intent_detection_node)
    workflow.add_node("retrieve", retrieve_context_node)
    workflow.add_node("reasoning", reasoning_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("generation", generation_node)
    workflow.add_node("emergency_escalation", emergency_escalation_node)
    workflow.add_node("proxy_gathering", proxy_gathering_node)
    workflow.add_node("skill_executor", skill_executor_node)
    workflow.add_node("audit", audit_node)
    workflow.add_node("persistence", persistence_node)

    # Define Entry Point
    workflow.set_entry_point("intent_detection")

    # Conditional routing based on detected intent and triaging zone
    def route_intent(state: ChatState) -> str:
        if state.intent_type == "emergency_escalation":
            return "emergency_escalation"
        if state.intent_type == "action":
            return "action"
        if state.low_data_mode:
            return "proxy_gathering"
        return "knowledge"

    workflow.add_conditional_edges(
        "intent_detection",
        route_intent,
        {
            "knowledge": "retrieve",
            "proxy_gathering": "proxy_gathering",
            "action": "skill_executor",
            "emergency_escalation": "emergency_escalation",
        }
    )

    # Definitive Knowledge path
    workflow.add_edge("retrieve", "reasoning")
    workflow.add_edge("reasoning", "validation")
    workflow.add_edge("validation", "generation")
    workflow.add_edge("generation", "audit")

    # Proxy gathering path
    workflow.add_edge("proxy_gathering", "audit")

    # Action execution path
    workflow.add_edge("skill_executor", "audit")

    # Red Zone Emergency escalation path
    workflow.add_edge("emergency_escalation", "audit")
    
    # Audit trail to persistent mirror ledger to END
    workflow.add_edge("audit", "persistence")
    workflow.add_edge("persistence", END)

    return workflow.compile()
