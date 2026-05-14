from langgraph.graph import StateGraph, END
from ..models.chat_state import ChatState
from .nodes.chat_nodes import retrieve_context_node, reasoning_node, generation_node, audit_node, proxy_gathering_node
from .nodes.intent_detector import intent_detection_node
from .nodes.skill_executor import skill_executor_node

def create_chat_pipeline():
    workflow = StateGraph(ChatState)

    # Add Nodes
    workflow.add_node("intent_detection", intent_detection_node)
    workflow.add_node("retrieve", retrieve_context_node)
    workflow.add_node("reasoning", reasoning_node)
    workflow.add_node("generation", generation_node)
    workflow.add_node("proxy_gathering", proxy_gathering_node)
    workflow.add_node("skill_executor", skill_executor_node)
    workflow.add_node("audit", audit_node)

    # Define Edges
    workflow.set_entry_point("intent_detection")

    # Conditional routing based on detected intent and low data state
    def route_intent(state: ChatState) -> str:
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
        }
    )

    # Knowledge path (existing)
    workflow.add_edge("retrieve", "reasoning")
    workflow.add_edge("reasoning", "generation")
    workflow.add_edge("generation", "audit")

    # Proxy gathering path (new)
    workflow.add_edge("proxy_gathering", "audit")

    # Action path (new)
    workflow.add_edge("skill_executor", "audit")
    
    workflow.add_edge("audit", END)

    return workflow.compile()

