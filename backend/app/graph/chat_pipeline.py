from langgraph.graph import StateGraph, END
from ..models.chat_state import ChatState
from .nodes.chat_nodes import retrieve_context_node, reasoning_node, generation_node, audit_node

def create_chat_pipeline():
    workflow = StateGraph(ChatState)

    # Add Nodes
    workflow.add_node("retrieve", retrieve_context_node)
    workflow.add_node("reasoning", reasoning_node)
    workflow.add_node("generation", generation_node)
    workflow.add_node("audit", audit_node)

    # Define Edges
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "reasoning")
    workflow.add_edge("reasoning", "generation")
    workflow.add_edge("generation", "audit")
    workflow.add_edge("audit", END)

    return workflow.compile()
