from ...models.state import GraphState
from langgraph.types import interrupt

def socratic_node(state: GraphState) -> GraphState:
    print("--- SOCRATIC RESOLUTION (HITL) ---")
    
    # We interrupt the graph to wait for expert input.
    # The 'value' passed to interrupt can be metadata about what needs resolution.
    expert_response = interrupt({
        "message": "Expert judgment required for synthetic scenarios.",
        "scenarios": [s.dict() for s in state.synthetic_scenarios]
    })
    
    # Once resumed, the expert_response will be available
    # expert_response should be the transcript or audio link provided by the UI
    print(f"--- RESUMED: Captured Expert Response ---")
    # Store response in state for the parser to use
    # (Handling list of responses if multiple scenarios)
    return state
