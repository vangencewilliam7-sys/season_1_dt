import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.graph.pipeline import create_pipeline
from app.models.state import GraphState

def verify():
    print("Initializing Knowledge Hub Pipeline...")
    app = create_pipeline()
    
    initial_state = GraphState(document_id="test-doc-123")
    
    print("Running pipeline...")
    # Using thread_id mock for stateful execution simulation if needed
    final_state = app.invoke(initial_state)
    
    print("Pipeline execution complete.")
    print(f"Final State Document ID: {final_state['document_id']}")
    return True

if __name__ == "__main__":
    try:
        verify()
    except Exception as e:
        print(f"Verification failed: {e}")
        sys.exit(1)
