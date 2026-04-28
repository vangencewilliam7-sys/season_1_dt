from langgraph.graph import StateGraph, END
from ..models.state import GraphState
from .nodes.ingestion import ingestion_node
from .nodes.divergence import divergence_node
from .nodes.slm_filter import slm_filter_node
from .nodes.socratic import socratic_node
from .nodes.parser import parser_node
from .nodes.audit import audit_node

from langgraph.checkpoint.memory import MemorySaver

# Global checkpointer so state persists across API requests
global_checkpointer = MemorySaver()

def create_pipeline():
    workflow = StateGraph(GraphState)

    # Add Nodes
    workflow.add_node("ingestion", ingestion_node)
    workflow.add_node("divergence", divergence_node)
    workflow.add_node("slm_filter", slm_filter_node)
    workflow.add_node("socratic", socratic_node) # Interrupt happens here
    workflow.add_node("parser", parser_node)
    workflow.add_node("audit", audit_node)

    # Define Edges
    workflow.set_entry_point("ingestion")
    workflow.add_edge("ingestion", "divergence")
    workflow.add_edge("divergence", "slm_filter")
    
    # Conditional edge from slm_filter (retry if hallucination)
    def should_retry(state: GraphState):
        from ..models.enums import AuditStatus
        # If any scenario failed audit and we haven't hit our retry limit
        has_conflicts = any(r.status == AuditStatus.CONFLICT for r in state.slm_audit_results)
        if has_conflicts and state.retry_count < 3:
            print(f"--- RETRYING Divergence (Attempt {state.retry_count}) ---")
            return "divergence"
        return "socratic"

    workflow.add_conditional_edges(
        "slm_filter",
        should_retry,
        {
            "divergence": "divergence",
            "socratic": "socratic"
        }
    )
    
    # ... (existing edges)
    workflow.add_edge("socratic", "parser")
    # Logic for Echo Verification Retry
    def check_audit_result(state: GraphState):
        from ..models.enums import AuditStatus
        # If any case failed the Echo Verification audit
        has_conflicts = any(r.status == AuditStatus.CONFLICT for r in state.audit_log if r.node == "visual_audit")
        
        if has_conflicts and state.retry_count < 3:
            print(f"--- ECHO VERIFICATION FAILED: Retrying Parse (Attempt {state.retry_count}) ---")
            state.retry_count += 1
            return "parser" 
        return "expert_gate" # Move to UI for final Expert review/sign-off

    workflow.add_conditional_edges(
        "audit",
        check_audit_result,
        {
            "parser": "parser",
            "expert_gate": END # Break here to allow the Expert to see the final parsed result in the UI
        }
    )

    return workflow.compile(checkpointer=global_checkpointer)
